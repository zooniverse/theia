import csv

def write_manifest(csv_filename, accepted):
    if not accepted or len(accepted) < 1:
        return

    with open(csv_filename, 'w') as csvfile:

        fieldnames = ['#filename', '#row', '#column']

        for key in sorted(accepted[0].keys()):
            if key == "#reason":
                continue

            if not key in fieldnames:
                fieldnames.append(key)

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

        writer.writeheader()

        for subject in accepted:
            writer.writerow(subject)


def write_rejects(csv_filename, rejects):
    if not rejects or len(rejects) < 1:
        return

    with open(csv_filename, 'w') as csvfile:

        fieldnames = ['#filename', '#reason', '#row', '#column']
        for key in sorted(rejects[0].keys()):
            if not key in fieldnames:
                fieldnames.append(key)

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

        writer.writeheader()

        for reject in rejects:
            writer.writerow(reject)
