import numpy as np
import influxdb_client, os, time
import matplotlib.pyplot as plt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from scipy.constants import precision
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, precision_score, recall_score, precision_recall_curve
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit


def get_series(measurement, field, location, range, as_np=True, aggregate='mean', aggregateWindow='5m'):
    query = f'from(bucket: "dewpointvc")\
      |> range({range})\
      |> filter(fn: (r) => r["_measurement"] == "{measurement}")\
      |> filter(fn: (r) => r["_field"] == "{field}")'
    if location is not None:
        query += f'|> filter(fn: (r) => r["location"] == "{location}")'
    query += f'|> aggregateWindow(every: {aggregateWindow}, fn: {aggregate}, createEmpty: false)\
      |> yield(name: "{aggregate}")\
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'

    tables = query_api.query_data_frame(query, org="toris")
    table = tables[0] if '_value' in tables[0].columns else tables[1]
    if as_np:
        return np.array(table['_value'])

    return table


def find_flanks(fan_status, before_n, after_n):
    fan_before = [np.concatenate([[True] * n, fan_status[:-n]]) for n in range(1, before_n + 1)]
    fan_after = [np.concatenate([fan_status[n:], [False] * n]) for n in range(1, after_n + 1)]

    flanks = np.logical_and.reduce([fan_status == True] + [np.logical_not(b) for b in fan_before] + fan_after)
    return np.where(flanks)[0]


def crop_flanks(arr, flanks, n_before, n_after):
    result = []
    for idx in flanks:
        if idx >= n_before and idx + n_after <= len(arr):
            result.append(arr[idx - n_before:idx + n_after])
    return np.stack(result)


def bin_scatter(x, y, binsize=0.005):
    bin_edges = np.arange(min(x), max(x) + binsize, binsize)

    # Step 2: Digitize the sizes to find which bin each size falls into
    bin_indices = np.digitize(x, bin_edges)

    # Step 3: Initialize a list to hold the mean IoU for each bin
    y_per_bin = []

    # Step 4: Loop over each bin and compute the mean IoU
    for i in range(1, len(bin_edges)):
        # Find indices of points that fall into this bin
        bin_mask = (bin_indices == i)

        # If there are points in the bin, calculate the mean IoU
        if np.any(bin_mask):
            y_per_bin.append(np.mean(y[bin_mask]))
        else:
            y_per_bin.append(np.nan)  # To handle empty bins

    # Step 5: Plot the bin centers and the mean IoUs
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2  # Calculate bin centers

    y_per_bin = np.array(y_per_bin)

    bin_centers = bin_centers[np.logical_not(np.isnan(y_per_bin))]
    y_per_bin = y_per_bin[np.logical_not(np.isnan(y_per_bin))]

    return bin_centers, y_per_bin


if __name__ == "__main__":
    token = 'bnyBnna3Hy2d0MRC9zmz8RbxpL7p-3uVqbJin3InV9lHNByapiLUQX0IYsFrbbi8oM5gCW6-Cbl9ubXDFaOM2g=='
    org = "toris"
    url = "http://localhost:8086"

    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    time_range = 'start: -100d'
    aggregateWindowMin = 5
    aggregateWindowStr = f'{aggregateWindowMin}m'
    dewpoint_cellar_np = get_series('temp_humidity', 'dewpoint', 'cellar', time_range, as_np=True,
                                    aggregateWindow=aggregateWindowStr)
    dewpoint_outside_np = get_series('temp_humidity', 'dewpoint', 'outside', time_range, as_np=True,
                                     aggregateWindow=aggregateWindowStr)
    humid_cellar_np = get_series('temp_humidity', 'relative_humidity', 'cellar', time_range, as_np=True,
                                 aggregateWindow=aggregateWindowStr)
    humid_outside_np = get_series('temp_humidity', 'relative_humidity', 'outside', time_range, as_np=True,
                                  aggregateWindow=aggregateWindowStr)
    temp_cellar_np = get_series('temp_humidity', 'temperature', 'cellar', time_range, as_np=True,
                                aggregateWindow=aggregateWindowStr)
    temp_outside_np = get_series('temp_humidity', 'temperature', 'outside', time_range, as_np=True,
                                 aggregateWindow=aggregateWindowStr)
    fan_status = get_series('fan_status', 'fan_state', None, time_range, aggregate='max', as_np=True,
                            aggregateWindow=aggregateWindowStr)

    after_n = 5
    flanks = find_flanks(fan_status, 2, after_n)
    if False:
        plt.figure()
        h1 = plt.subplot(311)
        plt.plot(fan_status, 'r-x')
        plt.plot(flanks, [1] * len(flanks), 'b x')

        plt.subplot(312, sharex=h1)
        plt.plot(temp_cellar_np, 'r-')
        plt.plot(temp_outside_np, 'b-')
        plt.plot(dewpoint_cellar_np, 'r-', alpha=0.5)
        plt.plot(dewpoint_outside_np, 'b-', alpha=0.5)
        plt.legend(['temp cellar', 'temp outside', 'DP cellar', 'DP outside'])
        plt.ylabel('dewpoint [°C]')

        plt.subplot(313, sharex=h1)
        plt.plot(humid_cellar_np, 'r-')
        plt.plot(humid_outside_np, 'b-')
        plt.plot(fan_status * 100, 'g-x', alpha=0.3)
        plt.plot(np.convolve(np.gradient(humid_cellar_np), np.ones(2) / 2, 'same'), 'r-')
        plt.ylabel('rel. humidity [%]')
        plt.legend(['cellar', 'outside', 'fan', 'humidgradient'])

        plt.show()

    if False:
        dewpoint_cellar_flanks = crop_flanks(dewpoint_cellar_np, flanks, 1, after_n)
        dewpoint_outside_flanks = crop_flanks(dewpoint_outside_np, flanks, 1, after_n)

        # dewpoint_diff_before = dewpoint_cellar_flanks[:, 0] - dewpoint_outside_flanks[:, 0]
        dewpoint_diff_before = dewpoint_cellar_flanks.mean(axis=1) - dewpoint_outside_flanks.mean(axis=1)

        dewpoint_cellar_flanks_rel_to_start = dewpoint_cellar_flanks - np.repeat(dewpoint_cellar_flanks[:, 0:1],
                                                                                 dewpoint_cellar_flanks.shape[1],
                                                                                 axis=1)

        plt.figure()
        h1 = plt.subplot(311)
        plt.plot(np.transpose(dewpoint_cellar_flanks_rel_to_start), 'r-x')
        plt.grid(True)

        plt.subplot(312)
        plt.plot(dewpoint_diff_before, dewpoint_cellar_flanks_rel_to_start[:, 1], 'r x')
        plt.xlabel('dewpoint diff')
        plt.ylabel(f'gradient after {aggregateWindowMin} min')
        plt.grid(True)
        plt.subplot(313)
        plt.plot(dewpoint_diff_before, dewpoint_cellar_flanks_rel_to_start[:, -1], 'r x')
        plt.xlabel('dewpoint diff')
        plt.ylabel(f'gradient after {after_n * aggregateWindowMin} min')
        plt.grid(True)
        plt.show()

    if False:
        humid_cellar_flanks = crop_flanks(humid_cellar_np, flanks, 1, after_n)
        humid_outside_flanks = crop_flanks(humid_outside_np, flanks, 1, after_n)

        # humid_diff_before = humid_cellar_flanks[:, 0] - humid_outside_flanks[:, 0]
        humid_diff_before = humid_cellar_flanks.mean(axis=1) - humid_outside_flanks.mean(axis=1)

        humid_cellar_flanks_rel_to_start = humid_cellar_flanks - np.repeat(humid_cellar_flanks[:, 0:1],
                                                                           humid_cellar_flanks.shape[1],
                                                                           axis=1)

        plt.figure()
        h1 = plt.subplot(511)
        plt.plot(np.transpose(humid_cellar_flanks_rel_to_start), 'r-x')
        plt.xlabel('time after ventilation [min]')
        plt.grid(True)
        plt.xticks(range(after_n + 1), [i * aggregateWindowMin for i in range(after_n + 1)])

        plt.subplot(512)
        plt.boxplot(humid_cellar_flanks_rel_to_start, whis=1.5, sym='')
        plt.xlabel('time after ventilation [min]')
        plt.xticks(range(1, after_n + 2), [(i) * aggregateWindowMin for i in range(after_n + 1)])
        plt.grid(True)

        plt.subplot(513)
        plt.plot(humid_diff_before, humid_cellar_flanks_rel_to_start[:, 1], 'r x')
        plt.xlabel('humidity diff (cellar - outside)')
        plt.ylabel(f'gradient after {aggregateWindowMin} min')
        plt.grid(True)

        plt.subplot(513)
        plt.plot(humid_diff_before, humid_cellar_flanks_rel_to_start[:, 2], 'r x')
        plt.xlabel('humidity diff (cellar - outside)')
        plt.ylabel(f'gradient after {2 * aggregateWindowMin} min')
        plt.grid(True)

        plt.subplot(514)
        plt.plot(humid_diff_before, humid_cellar_flanks_rel_to_start[:, -1], 'r x')
        plt.xlabel('humidity diff (cellar - outside)')
        plt.ylabel(f'gradient after {after_n * aggregateWindowMin} min')
        plt.grid(True)
        plt.show()

    if True:
        n_average = 1
        dewpoint_cellar_np_grad = np.gradient(dewpoint_cellar_np)
        dewpoint_cellar_np_grad = np.convolve(dewpoint_cellar_np_grad, np.ones(n_average) / n_average, 'same')
        humid_cellar_np_grad = np.gradient(humid_cellar_np)
        humid_cellar_np_grad = np.convolve(humid_cellar_np_grad, np.ones(n_average) / n_average, 'same')

        dew_point_diff = np.convolve(dewpoint_cellar_np - dewpoint_outside_np, np.ones(n_average) / n_average, 'same')
        humid_diff = np.convolve(humid_cellar_np - humid_outside_np, np.ones(n_average) / n_average, 'same')

        dewpoint_cellar_np_grad = dewpoint_cellar_np_grad[fan_status > 0]
        humid_cellar_np_grad = humid_cellar_np_grad[fan_status > 0]
        dew_point_diff = dew_point_diff[fan_status > 0]
        humid_diff = humid_diff[fan_status > 0]

        y = humid_cellar_np_grad < 0
        # y = dewpoint_cellar_np_grad < 0
        # y = np.logical_and(humid_cellar_np_grad < 0, dewpoint_cellar_np_grad < 0)

        X = np.stack([dew_point_diff,
                      humid_diff,
                      # temp_cellar_np[fan_status > 0],
                      # temp_outside_np[fan_status > 0],
                      # humid_cellar_np[fan_status > 0],
                      # humid_outside_np[fan_status > 0],
                      ]).T

        skf = StratifiedShuffleSplit(n_splits=1, test_size=0.5)
        train_index, test_index = next(skf.split(X, y))
        # train_index = slice(0, len(y) * 3 // 4)
        # test_index = slice(len(y) * 3 // 4, None)
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        # y_test_pred = humid_diff[test_index] > -5
        # y_test_pred = humid_diff[test_index] == humid_diff[test_index]

        cl = RandomForestClassifier(n_estimators=100, max_depth=6)
        cl.fit(X_train, y_train)
        print(f'feature importances: {cl.feature_importances_}')

        y_test_pred = cl.predict(X_test)
        y_test_pred_score = cl.predict_proba(X_test)[:, 1]
        precision, recall, thresholds = precision_recall_curve(y_test, y_test_pred_score)
        plt.figure()
        plt.plot(precision, recall)
        plt.xlabel('Precision')
        plt.ylabel('Recall')

        cm = confusion_matrix(y_test, y_test_pred)
        print('confusion matrix:')
        print(cm)
        print(f'precision: {precision_score(y_test, y_test_pred):0.2f}')
        print(f'recall: {recall_score(y_test, y_test_pred):0.2f}')

        dewpoint_cellar_np_grad = dewpoint_cellar_np_grad[test_index]
        humid_cellar_np_grad = humid_cellar_np_grad[test_index]
        dew_point_diff = dew_point_diff[test_index]
        humid_diff = humid_diff[test_index]

        plt.figure()
        h1 = plt.subplot(411)
        plt.plot(dew_point_diff, dewpoint_cellar_np_grad, 'r x')
        x, y = bin_scatter(dew_point_diff, dewpoint_cellar_np_grad, binsize=1)
        plt.plot(x, y, 'b-x')
        plt.xlabel('dewpoint diff (cellar - outside)')
        plt.ylabel('dewpoint gradient')
        plt.grid(True)

        plt.subplot(412)
        plt.plot(humid_diff, dewpoint_cellar_np_grad, 'r x')
        x, y = bin_scatter(humid_diff, dewpoint_cellar_np_grad, binsize=1)
        plt.plot(x, y, 'b-x')
        plt.xlabel('humid_diff diff (cellar - outside)')
        plt.ylabel('dewpoint gradient')
        plt.grid(True)

        plt.subplot(413)
        plt.plot(dew_point_diff[y_test_pred], humid_cellar_np_grad[y_test_pred], 'g x')
        plt.plot(dew_point_diff[y_test_pred == 0], humid_cellar_np_grad[y_test_pred == 0], 'r x')
        x, y = bin_scatter(dew_point_diff, humid_cellar_np_grad, binsize=1)
        plt.plot(x, y, 'b-x')
        plt.xlabel('dewpoint diff (cellar - outside)')
        plt.ylabel('humidity gradient')
        plt.grid(True)

        plt.subplot(414)
        plt.plot(humid_diff[y_test_pred], humid_cellar_np_grad[y_test_pred], 'g x')
        plt.plot(humid_diff[y_test_pred == 0], humid_cellar_np_grad[y_test_pred == 0], 'r x')
        x, y = bin_scatter(humid_diff, humid_cellar_np_grad, binsize=1)
        plt.plot(x, y, 'b-x')
        plt.xlabel('humid_diff diff (cellar - outside)')
        plt.ylabel('humidity gradient')
        plt.grid(True)

        plt.figure()
        plt.subplot(211)
        plt.title('prediction')
        plt.plot(humid_diff[y_test_pred], dew_point_diff[y_test_pred], 'g x')
        plt.plot(humid_diff[y_test_pred == 0], dew_point_diff[y_test_pred == 0], 'r x')
        plt.xlabel('humid_diff diff (cellar - outside)')
        plt.ylabel('dewpoint difference')
        plt.grid(True)

        plt.subplot(212)
        plt.title('ground truth')
        plt.plot(humid_diff[y_test], dew_point_diff[y_test], 'g x')
        plt.plot(humid_diff[y_test == 0], dew_point_diff[y_test == 0], 'r x')
        plt.xlabel('humid_diff diff (cellar - outside)')
        plt.ylabel('dewpoint difference')
        plt.grid(True)

        # fig = plt.figure()
        # ax = fig.add_subplot(projection='3d')
        # ax.scatter(dew_point_diff, humid_diff, humid_cellar_np_grad)
        # ax.set_xlabel('dewpoint difference')
        # ax.set_ylabel('humidity difference')
        # ax.set_zlabel('humidity gradient')

        plt.show()

        if True:
            plt.figure()
            h1 = plt.subplot(311)
            plt.plot(fan_status, 'r-x')
            plt.plot(flanks, [1] * len(flanks), 'b x')

            plt.subplot(312, sharex=h1)
            plt.plot(temp_cellar_np, 'r-')
            plt.plot(temp_outside_np, 'b-')
            plt.plot(dewpoint_cellar_np, 'r-', alpha=0.5)
            plt.plot(dewpoint_outside_np, 'b-', alpha=0.5)
            plt.legend(['temp cellar', 'temp outside', 'DP cellar', 'DP outside'])
            plt.ylabel('dewpoint [°C]')

            y_pred_fan = cl.predict(X)

            y_fan_new = (fan_status * 100).copy()
            # TODO: fix this assignment
            y_fan_new[y_fan_new>0][np.logical_not(y_pred_fan)] = 0


            plt.subplot(313, sharex=h1)
            plt.plot(humid_cellar_np, 'r-')
            plt.plot(humid_outside_np, 'b-')
            plt.plot(fan_status * 100, 'g-x', alpha=0.3)
            plt.plot(y_fan_new, 'b-x', alpha=0.3)
            plt.ylabel('rel. humidity [%]')
            plt.legend(['cellar', 'outside', 'fan', 'y_fan_new'])

            plt.show()
