# fm-synthesizer-pyo

A frequency modulation synthesizer, realized in Python with Pyo library. 

#### Needed library: **Pyo** - [official website](http://ajaxsoundstudio.com/software/pyo/)


>Pyo is a Python module written in C to help digital signal processing script creation. It provides a complete set of classes to build audio softwares, compose algorithmic musics or simply explore audio processing with a simple, mature and powerful programming language.

---

In my project I used four oscillators, the first and the second one module the carrier while third and fourth module the first and the second.

     ____            ____
    |    |          |    |
    | 3  |          |  4 |
    |____|          |____|
      ||              ||
      ||              ||
     _\/_            _\/_
    |    |          |    |
    | 1  |          |  2 |
    |____|          |____|
      ||              ||
      ||______________||
      \______ + _______/
             | |
            _\ /_
            |   |
            | C |
            |___|
             | |
             | |
             \ /
            OUTPUT

