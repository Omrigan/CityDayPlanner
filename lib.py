import json
moscow_radius = 20000
moscow_location = "55.753748,37.620688"
def pretty_json(inp):
    return json.dumps(inp, sort_keys=True, indent=4, ensure_ascii=False)

additional_fields = {
    'market': []
}