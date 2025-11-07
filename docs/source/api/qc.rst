Quality Control
===============

.. automodule:: iniamet.qc
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

The quality control module provides comprehensive data validation and quality checks for meteorological data.

Quick Reference
---------------

.. code-block:: python

   from iniamet import QualityControl, apply_quality_control
   
   # Apply quality control (easy way)
   clean_data = apply_quality_control(data, 'temperatura')
   
   # Advanced usage
   qc = QualityControl()
   flags = qc.run_all_checks(data, 'temperatura')

Classes
-------

.. autoclass:: iniamet.qc.QualityControl
   :members:
   :undoc-members:
   :special-members: __init__

Functions
---------

.. autofunction:: iniamet.qc.apply_quality_control

.. autofunction:: iniamet.qc.get_qc_report

Examples
--------

Basic Quality Control
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import apply_quality_control
   
   # Apply QC to temperature data
   clean_data = apply_quality_control(data, 'temperatura')
   
   print(f"Original: {len(data)} records")
   print(f"Clean: {len(clean_data)} records")
   print(f"Removed: {len(data) - len(clean_data)} records")

Advanced Quality Control
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import QualityControl
   
   qc = QualityControl()
   
   # Run individual checks
   extreme_flags = qc.detect_extreme_values(data, 'temperatura')
   stuck_flags = qc.detect_stuck_sensor(data)
   
   # Run all checks
   all_flags = qc.run_all_checks(data, 'temperatura')
   
   # View flagged data
   flagged = data[all_flags > 0]
   print(f"Flagged {len(flagged)} records")

Get QC Report
~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import get_qc_report
   
   # Get detailed report
   report = get_qc_report(data, 'temperatura')
   print(report)

Quality Check Types
-------------------

The module performs these checks:

1. **Extreme Values**: Detects values outside physically possible ranges
2. **Stuck Sensor**: Detects when sensors report the same value repeatedly
3. **Temporal Consistency**: Checks for unrealistic changes between readings
4. **Missing Data**: Flags missing or null values
5. **Suspicious Zeros**: Detects suspicious patterns of zero values

Thresholds
----------

Default thresholds for temperature:

* Min: -60°C
* Max: 60°C
* Persistence: 6 consecutive identical values
* Max change: 20°C per hour
