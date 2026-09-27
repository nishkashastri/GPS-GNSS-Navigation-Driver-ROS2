import utm

def parse_gpgga(sentence):
    sentence = sentence.strip()
    if '*' in sentence:
        sentence = sentence.split('*')[0]

    fields = sentence.split(',')

    if fields[6] == '0' or fields[6] == '':
        return None  # no fix, skip this sentence

    # --- Latitude ---
    lat_raw = fields[2]
    degrees = float(lat_raw[:2])
    minutes = float(lat_raw[2:])
    lat_decimal = degrees + minutes / 60
    if fields[3] == "S":
        lat_decimal = -lat_decimal

    # --- Longitude ---
    lon_raw = fields[4]
    degrees = float(lon_raw[:3])
    minutes = float(lon_raw[3:])
    lon_decimal = degrees + minutes / 60
    if fields[5] == "W":
        lon_decimal = -lon_decimal

    # --- Altitude ---
    altitude = float(fields[9])

    # --- UTM conversion ---
    easting, northing, zone_number, zone_letter = utm.from_latlon(lat_decimal, lon_decimal)

    return {
        'utc_time': fields[1],
        'latitude': lat_decimal,
        'longitude': lon_decimal,
        'altitude': altitude,
        'utm_easting': easting,
        'utm_northing': northing,
        'zone_number': zone_number,
        'zone_letter': zone_letter,
    }
