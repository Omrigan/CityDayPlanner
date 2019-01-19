for cat in additional_fields:
    for option in additional_fields[cat]:
        additional_fields[cat][option] = list(additional_fields[cat][option])
with open(ADDITIONAL_PATH, 'w') as f:
    f.write(pretty_json(additional_fields))

ADDITIONAL_PATH = 'process/additional.json'

additional_fields = defaultdict(lambda: defaultdict(set))

if os.path.isfile(ADDITIONAL_PATH):
    additional_fields_old = json.load(open(ADDITIONAL_PATH))
    for cat in additional_fields_old:
        for option in additional_fields_old[cat]:
            additional_fields[cat][option] = set(additional_fields_old[cat][option])


