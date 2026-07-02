# Figures Demo

Auto-generated figures demonstrating digraphx functionality.

## TinyDiGraph Example

```{plot} examples/plot_tiny_digraph.py
```

## Cycle Detection Example

```{plot} examples/plot_cycle_detection.py
```

### Inline Plot Example

```{plot}
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 100)
plt.plot(x, np.sin(x))
plt.title("Simple Sine Wave")
plt.grid(True, alpha=0.3)
```
