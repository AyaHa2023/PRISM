# Labelled outcomes for calibration

`labelled_outcomes_template.json` is an example schema, not measured business truth. Replace its values with outcomes reviewed by the internship supervisor or collected from an approved historical dataset before using them to claim predictive accuracy.

Each record contains:

- `scenario_id`
- `expected_stress` from 0 to 100
- `expected_trust` from 0 to 100
- `expected_sentiment`: `positive`, `neutral`, `negative`, or `mixed`

The evaluator compares these labels with simulation predictions and reports:

- stress mean absolute error
- trust mean absolute error
- sentiment accuracy

Do not present the template values as validated results.
