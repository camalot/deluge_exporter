import inspect
import json
import os
import time
import traceback

from metrics.config import DelugeMetricsConfig
from libs import settings
from libs.logger import Log
from libs.enums.loglevel import LogLevel
from collections import defaultdict
from deluge_client import DelugeRPCClient

from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily


class DelugeMetricsCollector(object):
  def __init__(self, config: DelugeMetricsConfig):
    _method = inspect.stack()[0][3]
    self._class = self.__class__.__name__
    self._module = os.path.basename(__file__)[:-3]
    self.settings = settings.Settings()
    self.namespace = "deluge"
    self.polling_interval_seconds = config.metrics["pollingInterval"]
    self.config = config
    log_level = LogLevel[self.settings.log_level.upper()]
    if not log_level:
      log_level = LogLevel.DEBUG
    self.log = Log(log_level)


  def get_libtorrent_status_metrics_meta(self):
    # deluge does not expose these:
    # import libtorrent
    # return [(x.name, x.type) for x in libtorrent.session_stats_metrics()]
    return {
      'has_incoming_connections': {
        'source': b'has_incoming_connections',
        'type': GaugeMetricFamily,
        'help': '0 as long as no incoming connections have been established on the listening socket. Every time you change the listen port, this will be reset to 0.',
        'conv': int,
      },

      'download_bytes_total': {
        'source': b'total_download',
        'type': CounterMetricFamily,
        'help': 'Total bytes downloaded from all torrents. Includes all protocol overhead.',
      },
      'upload_bytes_total': {
        'source': b'total_upload',
        'type': CounterMetricFamily,
        'help': 'Total bytes uploaded for all torrents. Includes all protocol overhead.',
      },

      'payload_download_bytes_total': {
        'source': b'total_payload_download',
        'type': CounterMetricFamily,
        'help': 'Downloaded bytes excluding BitTorrent protocol overhead.',
      },
      'payload_upload_bytes_total': {
        'source': b'total_payload_upload',
        'type': CounterMetricFamily,
        'help': 'Uploaded bytes excluding BitTorrent protocol overhead.',
      },

      'ip_overhead_download_bytes_total': {
        'source': b'total_ip_overhead_download',
        'type': CounterMetricFamily,
        'help': 'Estimated bytes of TCP/IP overhead for downloads.',
      },
      'ip_overhead_upload_bytes_total': {
        'source': b'total_ip_overhead_upload',
        'type': CounterMetricFamily,
        'help': 'Estimated bytes of TCP/IP overhead for uploads.',
      },

      'dht_download_bytes_total': {
        'source': b'total_dht_download',
        'type': CounterMetricFamily,
        'help': 'Total bytes sent to the DHT.',
      },
      'dht_upload_bytes_total': {
        'source': b'total_dht_upload',
        'type': CounterMetricFamily,
        'help': 'Total bytes received from the DHT.',
      },

      'tracker_download_bytes_total': {
        'source': b'total_tracker_download',
        'type': CounterMetricFamily,
        'help': 'Total bytes received from trackers.',
      },
      'tracker_upload_bytes_total': {
        'source': b'total_tracker_upload',
        'type': CounterMetricFamily,
        'help': 'Total traffic sent to trackers.',
      },

      'redundant_download_bytes_total': {
        'source': b'total_redundant_bytes',
        'type': CounterMetricFamily,
        'help': 'The number of bytes that has been received more than once.',
      },

      'failed_bytes_total': {
        'source': b'total_failed_bytes',
        'type': CounterMetricFamily,
        'help': 'The number of bytes that were downloaded and later failed the hash check.',
      },

      'peers': {
        'source': b'num_peers',
        'type': GaugeMetricFamily,
        'help': 'Current number of peer connections in the current session, including connections that are not yet fully open.',
      },
      'dead_peers': {
        'source': b'num_dead_peers',
        'type': GaugeMetricFamily,
        'help': 'Dead peers.',
      },
      'unchoked_peers': {
        'source': b'num_unchoked',
        'type': GaugeMetricFamily,
        'help': 'The current number of unchoked peers.',
      },

      'allowed_upload_slots': {
        'source': b'allowed_upload_slots',
        'type': GaugeMetricFamily,
        'help': 'The current allowed number of unchoked peers.',
      },

      'upload_queued_peers': {
        'source': b'up_bandwidth_queue',
        'type': GaugeMetricFamily,
        'help': 'The number of peers that are waiting for more bandwidth quota from the torrent rate limiter.',
      },
      'download_queued_peers': {
        'source': b'down_bandwidth_queue',
        'type': GaugeMetricFamily,
        'help': 'The number of peers that are waiting for more bandwidth quota from the torrent rate limiter.',
      },

      'upload_queued_bytes': {
        'source': b'up_bandwidth_bytes_queue',
        'type': GaugeMetricFamily,
        'help': 'The number of bytes the queued connections are waiting for to be able to send.',
      },
      'download_queued_bytes': {
        'source': b'down_bandwidth_bytes_queue',
        'type': GaugeMetricFamily,
        'help': 'The number of bytes the queued connections are waiting for to be able to receive.',
      },

      'disk_write_queued_peers': {
        'source': b'disk_write_queue',
        'type': GaugeMetricFamily,
        'help': 'The number of peers currently waiting on a disk write to complete before it receives any more data on the socket.',
      },
      'disk_read_queued_peers': {
        'source': b'disk_read_queue',
        'type': GaugeMetricFamily,
        'help': 'The number of peers currently waiting on a disk read to complete before it sends any more data on the socket.',
      },

      'dht_nodes': {
        'source': b'dht_nodes',
        'type': GaugeMetricFamily,
        'help': 'The number of nodes in the DHT routing table.',
      },
      'dht_cached_nodes': {
        'source': b'dht_node_cache',
        'type': GaugeMetricFamily,
        'help': 'The number of cached DHT nodes (used to replace the regular nodes in the routing table in case any of them becomes unresponsive).',
      },

      'dht_torrents': {
        'source': b'dht_torrents',
        'type': GaugeMetricFamily,
        'help': 'The number of torrents tracked by the DHT at the moment.',
      },

      'dht_estimated_global_nodes': {
        'source': b'dht_global_nodes',
        'type': GaugeMetricFamily,
        'help': 'An estimation of the total number of nodes in the DHT network.',
      },

      'dht_total_allocations': {
        'source': b'dht_total_allocations',
        'type': GaugeMetricFamily,
        'help': 'The number of nodes allocated dynamically for a particular DHT lookup. This represents roughly the amount of memory used by the DHT.',
      },

      'peerlist_size': {
        'source': b'peerlist_size',
        'type': GaugeMetricFamily,
        'help': 'The number of known peers across all torrents.',
      },

      'torrents': {
        'source': b'num_torrents',
        'type': GaugeMetricFamily,
        'help': 'The number of torrents in the session.',
      },
      'paused_torrents': {
        'source': b'num_paused_torrents',
        'type': GaugeMetricFamily,
        'help': 'The number of paused torrents in the session.',
      },
    }
  
  def new_metric_with_labels_and_value(self, metric, name, documentation, labels, value):
    assert isinstance(labels, dict)
    m = metric(name, documentation, labels=labels.keys())
    m.add_metric(labels.values(), value)
    return m


  def run_metrics_loop(self):
    """Metrics fetching loop"""
    _method = inspect.stack()[0][3]
    while True:
        try:
            self.log.debug(f"{self._module}.{self._class}.{_method}", f"Begin metrics fetch")
            self.collect()
            self.log.debug(f"{self._module}.{self._class}.{_method}", f"End metrics fetch")
            self.log.debug(
                f"{self._module}.{self._class}.{_method}",
                f"Sleeping for {self.polling_interval_seconds} seconds",
            )
            time.sleep(self.polling_interval_seconds)
        except Exception as ex:
            self.log.error(f"{self._module}.{self._class}.{_method}", str(ex), traceback.format_exc())

  def collect(self):
    _method = inspect.stack()[0][3]
    client = DelugeRPCClient(
      self.config.deluge['host'],
      self.config.deluge['rpcPort'],
      self.config.deluge['rpcUser'],
      self.config.deluge['rpcPassword'], 
    )
    client.connect()

    libtorrent_status_metrics = self.get_libtorrent_status_metrics_meta()
    libtorrent_status_metric_source_names = [x['source'] for x in libtorrent_status_metrics.values()]

    libtorrent_status_metric_values = client.call('core.get_session_status', libtorrent_status_metric_source_names)

    for metric, props in libtorrent_status_metrics.items():
      if libtorrent_status_metric_values:
        if props['source'] in libtorrent_status_metric_values:
          value = libtorrent_status_metric_values[props['source']]
          if 'conv' in props:
            value = props['conv'](value)
          yield props['type'](f'{self.namespace}_libtorrent_{metric}', props['help'], value=value)
        else:
          yield props['type'](f'{self.namespace}_libtorrent_{metric}', props['help'], value=0)
          self.log.info(
            f"{self._module}.{self._class}.{_method}",
            f"metric '{metric}' not found in libtorrent_status_metric_values",
          )

    yield self.new_metric_with_labels_and_value(GaugeMetricFamily, f'{self.namespace}_info', 'Deluge information',
      labels={
        'version': client.call('daemon.info').decode("utf-8"),
        'libtorrent_version': client.call('core.get_libtorrent_version').decode("utf-8"),
      },
      value=1
    )

    for key, value in client.call('core.get_config').items():
      if isinstance(value, (int, float, bool)):
        yield GaugeMetricFamily(
          f'{self.namespace}_config_{key.decode("utf-8")}', 
          f'Value of the deluge config setting {key.decode("utf-8")}', 
          value=value,
        )

    torrents_by_state = {
      'downloading': 0,
      'seeding': 0,
      'paused': 0,
      'checking': 0,
      'queued': 0,
      'error': 0,
      'active': 0,
      # not the prometheus way, but the states above (as defined by deluge) are already overlapping, so sum() over them is already meaningless
      'total': 0,
    }
    torrents_by_label = defaultdict(int)
    for torrent in client.core.get_torrents_status(
          {}, [b'label', b'state', b'download_payload_rate', b'upload_payload_rate']
        ).values():
      if b'label' in torrent:
        torrents_by_label[torrent[b'label'].decode('utf-8')] += 1
      torrents_by_state[torrent[b'state'].decode('utf-8').lower()] += 1
      torrents_by_state['total'] += 1
      if torrent[b'download_payload_rate'] > 0 or torrent[b'upload_payload_rate'] > 0:
        torrents_by_state['active'] += 1

    if len(torrents_by_label) > 0:
      torrents_by_label_metric = GaugeMetricFamily(
        f'{self.namespace}_torrents_by_label', 
        'The number of torrents for each label assigned to a torrent using the deluge label plugin', 
        labels=['label'],
      )
      for label, count in torrents_by_label.items():
        torrents_by_label_metric.add_metric([label], count)
      yield torrents_by_label_metric

    torrents_metric = GaugeMetricFamily(
      f'{self.namespace}_torrents', 
      'The number of torrents in a specific state (note: some states overlap)', 
      labels=['state'],
    )
    for state, torrent_count in torrents_by_state.items():
      torrents_metric.add_metric([state], torrent_count)
    yield torrents_metric

    client.disconnect()