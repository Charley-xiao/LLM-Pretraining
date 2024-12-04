import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define a smoother convex surface function
def smoother_convex_surface_function(x, y):
    return (x**2 + y**2) ** 1.7

# Generate grid for the surface
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
Z = smoother_convex_surface_function(X, Y)

# Define points w*, w_A, w_B, w_0
w_star = np.array([0, 0])  # The lowest point (approximated for visualization)
w_A = np.array([-1, -1]) 
w_B = np.array([-0.5, -0.5]) 
w_0 = np.array([2.5, -2])  
tilde_w_B = np.array([2, 2])
tilde_w_A = np.array([0.6, 0.6])
w_A_star = np.array([-1.5, -0.9])
w_B_star = np.array([1.9, 2.5])

# Create curves w_0 -> w_A -> w* and w_0 -> w_B -> w*
def interpolate_points(start, mid, end, num_points=50, noise_level=0.05):
    # Interpolate from start to mid to end with noise
    t1 = np.linspace(0, 1, num_points // 2)
    t2 = np.linspace(0, 1, num_points // 2)
    path1 = (1 - t1[:, None]) * start + t1[:, None] * mid
    path2 = (1 - t2[:, None]) * mid + t2[:, None] * end
    
    # Add noise
    noise1 = noise_level * (np.random.rand(*path1.shape) - 0.5)
    noise2 = noise_level * (np.random.rand(*path2.shape) - 0.5)
    path1 += noise1
    path2 += noise2
    
    return np.vstack([path1, path2])

curve_A = interpolate_points(w_0, w_A, w_B)
curve_B = interpolate_points(w_0, tilde_w_B, tilde_w_A)

# Get Z values for the curves
curve_A_z = smoother_convex_surface_function(curve_A[:, 0], curve_A[:, 1])
curve_B_z = smoother_convex_surface_function(curve_B[:, 0], curve_B[:, 1])

# Plot the 3D convex surface with updated colors and arrow annotations
# Adjust plotting to make paths and points more prominent

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot the smoother convex surface with reduced alpha for better visibility of paths
ax.plot_surface(X, Y, Z, cmap='coolwarm', alpha=0.6)

# Plot the curves with arrows and make them more prominent
for i in range(len(curve_A) - 1):
    ax.quiver(
        curve_A[i, 0],
        curve_A[i, 1],
        curve_A_z[i],
        curve_A[i + 1, 0] - curve_A[i, 0],
        curve_A[i + 1, 1] - curve_A[i, 1],
        curve_A_z[i + 1] - curve_A_z[i],
        color="red",
        arrow_length_ratio=0.0,
        linewidth=2,
    )
for i in range(len(curve_B) - 1):
    ax.quiver(
        curve_B[i, 0],
        curve_B[i, 1],
        curve_B_z[i],
        curve_B[i + 1, 0] - curve_B[i, 0],
        curve_B[i + 1, 1] - curve_B[i, 1],
        curve_B_z[i + 1] - curve_B_z[i],
        color="blue",
        arrow_length_ratio=0.0,
        linewidth=2,
    )

# Mark the points with larger sizes and brighter colors
ax.scatter(*w_star, smoother_convex_surface_function(*w_star), color='gold', s=150, zorder=5, edgecolor='black', label='w*')
ax.text(*w_star, smoother_convex_surface_function(*w_star) + 10.5, 'w*', color='black', fontsize=10, ha='center')

ax.scatter(*w_A, smoother_convex_surface_function(*w_A), color='red', s=100, zorder=5, edgecolor='black', label='$w_A$')
ax.text(*w_A, smoother_convex_surface_function(*w_A) + 10.5, '$w_A$', color='black', fontsize=10, ha='center')

ax.scatter(*w_B, smoother_convex_surface_function(*w_B), color='blue', s=100, zorder=5, edgecolor='black', label='$w_B$')
ax.text(*w_B, smoother_convex_surface_function(*w_B) + 10.5, '$w_B$', color='black', fontsize=10, ha='center')

ax.scatter(*w_0, smoother_convex_surface_function(*w_0), color='green', s=100, zorder=5, edgecolor='black', label='$w_0$')
ax.text(*w_0, smoother_convex_surface_function(*w_0) + 10.5, '$w_0$', color='black', fontsize=10, ha='center')

ax.scatter(*tilde_w_B, smoother_convex_surface_function(*tilde_w_B), color='blue', s=100, zorder=5, edgecolor='black', label='$\widetilde{w}_B$')
ax.text(*tilde_w_B, smoother_convex_surface_function(*tilde_w_B) + 10.5, '$\widetilde{w}_B$', color='black', fontsize=10, ha='center')

ax.scatter(*tilde_w_A, smoother_convex_surface_function(*tilde_w_A), color='red', s=100, zorder=5, edgecolor='black', label='$\widetilde{w}_A$')
ax.text(*tilde_w_A, smoother_convex_surface_function(*tilde_w_A) + 10.5, '$\widetilde{w}_A$', color='black', fontsize=10, ha='center')

ax.scatter(*w_A_star, smoother_convex_surface_function(*w_A_star), color='red', s=100, zorder=5, edgecolor='black', label='$w_A^*$')
ax.text(*w_A_star, smoother_convex_surface_function(*w_A_star) + 10.5, '$w_A^*$', color='black', fontsize=10, ha='center')

ax.scatter(*w_B_star, smoother_convex_surface_function(*w_B_star), color='blue', s=100, zorder=5, edgecolor='black', label='$w_B^*$')
ax.text(*w_B_star, smoother_convex_surface_function(*w_B_star) + 10.5, '$w_B^*$', color='black', fontsize=10, ha='center')

# Labels and title

# Labels and legend
ax.set_title("Smooth Convex Surface with Prominent Paths to w*", fontsize=14)
ax.set_xlabel("First dimension of $w$")
ax.set_ylabel("Second dimension of $w$")
ax.set_zlabel("Loss $L(w)$")
ax.legend()

plt.show()
