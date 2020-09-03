-----------------

<p align="center">
  <img src="optimizer_app.mp4" width="700" height="550"/>
</p>

------------------
[![Build Status](https://travis-ci.org/russelljjarvis/BluePyOpt.svg?branch=master)](https://travis-ci.org/russelljjarvis/BluePyOpt)
------------------
# BluePyOpt: Blue Brain Python Optimisation Library

<table>
<tr>
  <td>Latest Release</td>
  <td>
    <a href="https://pypi.org/project/bluepyopt/">
    <img src="https://img.shields.io/pypi/v/bluepyopt.svg" alt="latest release" />
    </a>
  </td>
</tr>
<tr>
  <td>Documentation</td>
  <td>
    <a href="https://bluepyopt.readthedocs.io/">
    <img src="https://readthedocs.org/projects/bluepyopt/badge/?version=latest" alt="latest documentation" />
    </a>
  </td>
</tr>
<tr>
  <td>License</td>
  <td>
    <a href="https://github.com/BlueBrain/bluepyopt/blob/master/LICENSE.txt">
    <img src="https://img.shields.io/pypi/l/bluepyopt.svg" alt="license" />
    </a>
</td>
</tr>
<tr>
  <td>Build Status</td>
  <td>
    <a href="https://travis-ci.org/BlueBrain/BluePyOpt">
    <img src="https://travis-ci.org/BlueBrain/BluePyOpt.svg?branch=master" alt="travis build status" />
    </a>
  </td>
</tr>
<tr>
  <td>Coverage</td>
  <td>
    <a href="https://codecov.io/gh/BlueBrain/bluepyopt">
    <img src="https://codecov.io/github/BlueBrain/BluePyOpt/coverage.svg?branch=master" alt="coverage" />
    </a>
  </td>
</tr>
<tr>
	<td>Gitter</td>
	<td>
		<a href="https://gitter.im/bluebrain/bluepyopt">
		<img src="https://badges.gitter.im/Join%20Chat.svg"
	</a>
	</td>
</tr>
</table>

Introduction
============

The Blue Brain Python Optimisation Library (BluePyOpt) is an extensible
framework for data-driven model parameter optimisation that wraps and
standardises several existing open-source tools.

It simplifies the task of creating and sharing these optimisations,
and the associated techniques and knowledge.
This is achieved by abstracting the optimisation and evaluation tasks
into various reusable and flexible discrete elements according to established
best-practices.

Further, BluePyOpt provides methods for setting up both small- and large-scale
optimisations on a variety of platforms,
ranging from laptops to Linux clusters and cloud-based compute infrastructures.

Citation
========

When you use the BluePyOpt software or method for your research, we ask you to cite the following publication (**this includes poster presentations**):

[Van Geit W, Gevaert M, Chindemi G, Rössert C, Courcol J, Muller EB, Schürmann F, Segev I and Markram H (2016). BluePyOpt: Leveraging open source software and cloud infrastructure to optimise model parameters in neuroscience. Front. Neuroinform. 10:17. doi: 10.3389/fninf.2016.00017](http://journal.frontiersin.org/article/10.3389/fninf.2016.00017)

```bibtex
@ARTICLE{bluepyopt,
 AUTHOR={Van Geit, Werner  and  Gevaert, Michael  and  Chindemi, Giuseppe  and  Rössert, Christian  and  Courcol, Jean-Denis  and  Muller, Eilif Benjamin  and  Schürmann, Felix  and  Segev, Idan  and  Markram, Henry},   
TITLE={BluePyOpt: Leveraging open source software and cloud infrastructure to optimise model parameters in neuroscience},
JOURNAL={Frontiers in Neuroinformatics},
VOLUME={10},
YEAR={2016},
NUMBER={17},
URL={http://www.frontiersin.org/neuroinformatics/10.3389/fninf.2016.00017/abstract},
DOI={10.3389/fninf.2016.00017},
ISSN={1662-5196}
}
```
Support
=======
We are providing support using a chat channel on [Gitter](https://gitter.im/BlueBrain/BluePyOpt).

News
====
- 2017/01/04: BluePyOpt is now considered compatible with Python 3.6+.
- 2016/11/10: BluePyOpt now supports NEURON point processes. This means we can fit parameters of Adex/GIF/Izhikevich models, and also synapse models.
- 2016/06/14: Started a wiki: https://github.com/BlueBrain/BluePyOpt/wiki
- 2016/06/07: The BluePyOpt paper was published in Frontiers in Neuroinformatics (for link, see above)
- 2016/05/03: The API documentation was moved to [ReadTheDocs](http://bluepyopt.readthedocs.io/en/latest/)
- 2016/04/20: BluePyOpt now contains the code of the IBEA selector, no need to install a BBP-specific version of DEAP anymore
- 2016/03/24: Released version 1.0

Requirements
============

* [Python 2.7+](https://www.python.org/download/releases/2.7/) or [Python 3.6+](https://www.python.org/downloads/release/python-360/)
* [Pip](https://pip.pypa.io) (installed by default in newer versions of Python)
* [Neuron 7.4+](http://neuron.yale.edu/) (compiled with Python support)
* [eFEL eFeature Extraction Library](https://github.com/BlueBrain/eFEL) (automatically installed by pip)
* [Numpy](http://www.numpy.org) (automatically installed by pip)
* [Pandas](http://pandas.pydata.org/) (automatically installed by pip)
* The instruction below are written assuming you have access to a command shell
on Linux / UNIX / MacOSX / Cygwin

Installation
============

If you want to use the ephys module of BluePyOpt, you first need to install NEURON with Python support on your machine.

And then bluepyopt itself:

```bash
pip install bluepyopt
```

Cloud infrastructure
====================

We provide instructions on how to set up an optimisation environment on cloud
infrastructure or cluster computers
[here](https://github.com/BlueBrain/BluePyOpt/tree/master/cloud-config)

Quick Start
===========

Single compartmental model
--------------------------

An iPython notebook with an introductory optimisation of a one compartmental
model with 2 HH channels can be found at

https://github.com/BlueBrain/BluePyOpt/blob/master/examples/simplecell/simplecell.ipynb

![Landscape example](https://github.com/BlueBrain/BluePyOpt/blob/master/examples/simplecell/figures/landscape_example.png)
**Figure**: The solution space of a single compartmental model with two parameters: the maximal conductance of Na and K ion channels. The color represents how well the model fits two objectives: when injected with two different currents, the model has to fire 1 and 4 action potential respectively during the stimuli. Dark blue is the best fitness. The blue circles represent solutions with a perfect score.

Neocortical Layer 5 Pyramidal Cell
----------------------------------
Scripts for a more complex neocortical L5PC are in
[this directory](https://github.com/BlueBrain/BluePyOpt/tree/master/examples/l5pc)

With a notebook:

https://github.com/BlueBrain/BluePyOpt/blob/master/examples/l5pc/L5PC.ipynb

Thalamocortical Cells
---------------------
Scripts for 2 thalamocortical cell types are in
[this directory](https://github.com/BlueBrain/BluePyOpt/tree/master/examples/thalamocortical-cell)

With a notebook:

https://github.com/BlueBrain/BluePyOpt/blob/master/examples/thalamocortical-cell/thalamocortical-cell_opt.ipynb


Tsodyks-Markram Model of Short-Term Plasticity
---------------------
Scripts for 2 version of fitting the Tsodyks-Markram model to synaptic traces are in
[this directory](https://github.com/BlueBrain/BluePyOpt/tree/master/examples/tsodyksmarkramstp)

With 2 notebooks:

https://github.com/BlueBrain/BluePyOpt/blob/master/examples/tsodyksmarkramstp/tsodyksmarkramstp.ipynb
https://github.com/BlueBrain/BluePyOpt/blob/master/examples/tsodyksmarkramstp/tsodyksmarkramstp_multiplefreqs.ipynb

API documentation
==================
The API documentation can be found on [ReadTheDocs](http://bluepyopt.readthedocs.io/en/latest/).

Funding
=======
This work has been partially funded by the European Union Seventh Framework Program (FP7/2007­2013) under grant agreement no. 604102 (HBP), the European Union’s Horizon 2020 Framework Programme for Research and Innovation under the Specific Grant Agreement No. 720270, 785907 (Human Brain Project SGA1/SGA2).
