# Satisfaction Degree for Computation-Tree Logic over Multivalued Gene Regulatory Networks

This repository contains a prototype implementation of a novel algorithm for computing real-valued satisfaction degrees of Computation Tree Logic (CTL) formulas evaluated over Multivalued Gene Regulatory Networks (MvGRNs). Traditional temporal logic model checking offers only binary outcomes—either a property holds or not—which can be insufficient for analyzing complex biological systems where near-satisfaction or near-violation carries important insight. By integrating signed distance propagation into CTL semantics, this tool provides a more expressive analysis, quantifying how much a temporal logic property is satisfied or violated. The approach is grounded in a restricted but expressive fragment of CTL.

This project was developed as part of my Master's thesis at Faculty of Informatics, Masaryk University, Brno under the supervision of doc. RNDr. David Šafránek, Ph.D.

## Structure of the repository:

```
CTL_sat_degree/
├── data/
│ ├── incoherent_ffl1.json
│ ├── incoherent_ffl2.json
│ ├── incoherent_ffl3.json
│ ├── incoherent_ffl4.json
│ ├── predator_prey1.json
│ ├── predator_prey2.json
│ └── single_input_module.json
├── src/
│ ├── ctl_formulae.py
│ ├── custom_types.py
│ ├── kripke_structure.py
│ ├── lark_ctl_parser.py
│ ├── main.py
│ ├── multivalued_grn.py
│ ├── priority_queue.py
│ ├── weighted_distance.py
│ └── test/
│   ├── formula_methods_test.py
│   ├── mvgrn_test.py
│   ├── parser_test.py
│   ├── priority_queue_test.py
│   └── weighted_distance_test.py
├── stg/
│ ├── incoherent_ffl1.png
│ ├── incoherent_ffl2.png
│ ├── incoherent_ffl3.png
│ ├── incoherent_ffl4.png
│ ├── predator_prey1.png
│ ├── predator_prey2.png
│ └── single_input_module.png
└──
```

## Dependencies

This project uses Python 3.9+ and the following libraries:

- `lark` – for parsing CTL formulas
- `networkx` – for graph representations

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Execution

The algorithm can be executed from the command line as follows:

```bash
python main.py path/to/input.json
```
