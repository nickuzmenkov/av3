import matplotlib.pyplot as plt
import numpy as np

data = []
with open('data3d.txt', 'r') as file:
	data = [x.split() for x in file.readlines()[4:1004]]

data = np.asarray(data).astype('float32')

def pre(data, tau=2.375, den=1.225, vis=3.12e-5):
	u_star = (tau/den) ** .5
	u_plus = data[:,0] / u_star
	y_plus = (.005 - data[:,1]) * u_star * den / vis
	return y_plus, u_plus

y_plus, u_plus = pre(data)

x = np.linspace(0, 5)
plt.plot(y_plus, u_plus)
plt.plot(x, x, linestyle=':', color='red')
plt.xlim([0, 5])
plt.xlabel('y+')
plt.ylabel('u+')
plt.grid()
plt.show()

plt.clf()

x1 = np.linspace(0, 5)
x2 = np.linspace(5, 30)
y2 = 5 * np.log(x2) - 3.05
x3 = np.linspace(30, 500)
y3 = 2.5 * np.log(x3) + 5.5
plt.semilogx(y_plus, u_plus, color='blue')
plt.semilogx(x1, x1, linestyle=':', color='red')
plt.semilogx(x2, y2, linestyle=':', color='red')
plt.semilogx(x3, y3, linestyle=':', color='red')


plt.xlabel('y+')
plt.ylabel('u+')
plt.grid()
plt.show()