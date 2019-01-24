from dl import metric as metric_dl

from cassandra.cluster import Cluster
from google.cloud import bigtable

import argparse
import random
import threading
import time


def emit_metrics(server, cass_session, bt_session, bt_omit):
    count = 0
    while True:
        count += 1
        metric = metric_dl.Metric(server)
        cass_session.insert_row_cassandra(metric)
        if not bt_omit:
            bt_session.insert_row_bigtable(metric)
        print('Server {} emitted total {} metric'.format(server, count))
        time.sleep(random.randrange(5, 9))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '--servers',
        type=int,
        help='Number of servers to simulate',
        default=1)
    parser.add_argument(
        '--cassandra_host',
        help='Cassandra endpoint',
        required=True)
    parser.add_argument(
        '--cassandra_db',
        help='Cassandra keyspace',
        required=True)
    parser.add_argument(
        '--bt_project_id',
        help='Bigtable project id',
        required=True)
    parser.add_argument(
        '--bt_instance_id',
        help='Bigtable instance id',
        required=True)
    parser.add_argument(
        '--bt_omit',
        help='Insert to bigtable',
        action='store_true',
        default=False)

    args = parser.parse_args()

    # Cassandra connection
    cass_session = metric_dl.CassandraMetric(args.cassandra_host, args.cassandra_db)

    # Bigtable connection
    bt_session = None
    if args.bt_omit:
        bt_session = None
    else:
        bt_session = metric_dl.BigtableMetric(args.bt_project_id, args.bt_instance_id, )
        bt_client = bigtable.Client(project=args.bt_project_id, admin=True)
        bt_instance = bt_client.instance(args.bt_instance_id)
        bt_table = bt_instance.table(metric_dl.TABLE_NAME)

    num_of_servers = args.servers

    servers = [random.randrange(0, 2**32) for _ in range(num_of_servers)]
    print('=bringing up servers {}'.format(servers))
    for server in servers:
        thread = threading.Thread(target=emit_metrics, args=(server, cass_session, bt_session, args.bt_omit))
        thread.start()

