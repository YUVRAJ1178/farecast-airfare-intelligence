import sys
sys.path.insert(0, '.')
from ml.predict import get_predictor

p = get_predictor()
print('Model:', p._model_name)
print('RF available:', p._rf_pipeline is not None)
print()

tests = [
    ('IndiGo',         'DEL', 'BOM', 'Economy',  0,  1, 135,  6, '6k-9k last-min'),
    ('IndiGo',         'DEL', 'BOM', 'Economy',  0,  7, 135,  6, '4.5k-7k 1wk'),
    ('IndiGo',         'DEL', 'BOM', 'Economy',  0, 30, 135, 10, '3.5k-4.8k early-bird'),
    ('Air India',      'DEL', 'BOM', 'Economy',  0,  1, 135, 18, '8k-12k lastmin eve'),
    ('Air India',      'DEL', 'BOM', 'Business', 0, 14, 135, 10, '40k-60k biz'),
    ('Vistara',        'DEL', 'BLR', 'Economy',  0,  7, 165,  7, '4k-7k'),
    ('Vistara',        'BOM', 'DEL', 'Business', 0, 30, 135, 10, '40k-60k'),
    ('IndiGo',         'BOM', 'BLR', 'Economy',  0,  3, 100,  8, '5k-8k'),
    ('Air India',      'DEL', 'CCU', 'Economy',  0, 21, 130,  9, '5k-7.5k'),
    ('Air India',      'DEL', 'CCU', 'Economy',  0,  2, 130,  8, '8k-13k 2-day'),
    ('SpiceJet',       'DEL', 'BOM', 'Economy',  0, 14, 135, 14, '4k-6k'),
    ('GO FIRST',       'DEL', 'BOM', 'Economy',  0, 21, 135, 11, '3k-5k'),
    ('AirAsia India',  'DEL', 'BLR', 'Economy',  0, 35, 165,  2, '2.5k-4k redeye early'),
    ('Unknown Airline','DEL', 'BOM', 'Economy',  0,  7, 135,  9, 'unknown airline'),
    ('IndiGo',         'AMD', 'BOM', 'Economy',  0, 10,  60,  8, 'unknown route'),
]

print('%-18s %-10s %-12s %5s %8s %20s %-8s %-18s %s' % (
    'Airline', 'Route', 'Class', 'Days', 'Pred', 'Range', 'Conf', 'Method', 'Expected'))
print('-' * 115)
for airline, orig, dest, cabin, stops, dl, dur, dep, expected in tests:
    r = p.predict(airline, orig, dest, cabin, stops, dl, dur, dep)
    rng = '%d-%d' % (r.lower_bound, r.upper_bound)
    print('%-18s %-10s %-12s %5d %8.0f %20s %-8s %-18s %s' % (
        airline, orig+'-'+dest, cabin, dl, r.predicted_fare, rng, r.confidence, r.lookup_method or '', expected))
