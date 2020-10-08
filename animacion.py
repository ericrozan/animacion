import numpy as np
import math
import random
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import pylab
import os 

golden_mean = (math.sqrt(5)-1.0)/2.0        # Aesthetic ratio
#fig_width = 3+3/8                # width  in inches
fig_width=8
fig_height = fig_width#*golden_mean          # height in inches
fig_size =  [fig_width,fig_height]
#fontsize=8 #original
fontsize=13 #yo
params = {'backend': 'ps',
          'axes.titlesize': fontsize,
          'axes.labelsize': fontsize,
          'axes.linewidth': 0.75, 
          'axes.grid': False,
          'axes.labelweight': 'normal',  
          'font.family': 'serif',
          'font.size': fontsize,
          'font.weight': 'normal',
          'text.color': 'black',
          'xtick.labelsize': fontsize,
          'ytick.labelsize': fontsize,
          'text.usetex': True,
          'legend.fontsize': fontsize,
          'figure.dpi': 300,
          'figure.figsize': fig_size,
          'savefig.dpi': 300,
         }

pylab.rcParams.update(params)

def extract_data(file,idscol,typescol,xcol,ycol,c1col,tcol,Ncols):
	data = np.genfromtxt(file, delimiter = ' ')
	'''		
	Primero ordeno por ids, luego por tiempo. Es decir las primeras N filas
	corresponden al timestep 1, entre N+1 y 2N al timestep 2, etc.
	lexsort opera en orden inverso. [:,0] seria la ultima columna, y [:,N] la primera.
	Por lo tanto, columna i es [:,N-i]
	'''

	ix = np.lexsort((data[:, Ncols-tcol], data[:,Ncols-idscol])) 
	#	Estos son los indices de las columnas ordenados
	data=data[ix]
	#	Ahora si, finalmente, separar cada columna
	ids=data[:,idscol]
	types=data[:,typescol].astype(int)
	xx=data[:,xcol]
	yy=data[:,ycol]
	c1=data[:,c1col]
	c1=np.array(c1)>0
	tt=data[:,tcol]
	N=int(max(ids)) #Cantidad de personas
	M=int(len(ids)/N) #Cantidad de timesteps

	#	Quiero un vector Types que sea de long N, y corresponda al type de cada persona
	types=types[0:N]


	return ids,types,xx,yy,c1,tt,N,M


def asigna_colores(types):
	Ntypes=max(types)
	N=len(types)
	type_color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(Ntypes)]
	#	type_color es un vector de longitud Ntypes, que le asigna un color random a cada type
	colores=[] 	#Este vector de longitud N sera el que le asigne un color a cada persona
	for i in range(N):
		colores+=[type_color[types[i]-1]]
	return colores


def grafica_timestep_j(j,N,xx,yy,tt,colores,c1,width,length,door_min,door_max):
	x=xx[N*j:N*(j+1)]
	y=yy[N*j:N*(j+1)]
	if len(c1)!=N:
		c1=c1[N*j:N*(j+1)] 
	#	Este vector es el c1 en  el timestep j. Si c1 tiene
	#	longitud N es porque es el mismo para todo timestep
	
	t=tt[N*j]

	#### PARAMETERS #####
	xi_obst = 46.32
	xf_obst = 53.68
	yi_obst = 97.7
	yf_obst = 97.7
	
	
	lin=5 	#Ancho de linea del recinto

	#plt.plot([0,length],[0,0],'k',lw=lin)
	#plt.plot([0,length],[width,width],'k',lw=lin)
	#plt.plot([0,0],[0,width],'k',lw=lin)

	plt.plot([0,door_min],[width,width],'k',lw=lin)
	plt.plot([door_max,length],[width,width],'k',lw=lin)

	plt.plot([xi_obst,xf_obst],[yi_obst,yf_obst],'k',lw=lin)

	#	Elegir el tamanio de las personas:	
	size= 100 #650 	#zoom en la puerta
	#size=30 	#vista de lejos
	
	plt.scatter(x,y,edgecolor='black',lw=c1*3.5,s=size,color=colores,alpha=1)

	plt.axes().xaxis.set_tick_params(which='both', top = True,direction='out')
	plt.axes().yaxis.set_tick_params(which='both', top = True,direction='out')
	#plt.xticks(np.arange(0,length+1,1))
	#plt.yticks(np.arange(0,width+1,1))

	#	Zoom en la puerta
	plt.xlim(40,60)
	plt.ylim(90,102)

	#	Vista de lejos
	#plt.xlim(0,length)
	#plt.ylim(0,width)

	pylab.xlabel('x (m)')
	pylab.ylabel('y (m)')
	plt.title('t =%05.2f'%(t))

def from_pic_to_vid(video_filename,output_folder,framerate):
	'''	
	Esta funcion hace un video a partir de la secuencia de imagenes y luego borra las imagenes
	'''

	comando_para_movie = "ffmpeg -framerate {} -f image2 -pattern_type glob -i '*.png' {}.mp4".format(framerate,video_filename)
	os.system('cd {};{};rm *.png'.format(output_folder,comando_para_movie))


def main():
	######################## PARAMETERS ######################## 
	file='config_movie.txt'
	#	En este archivo noheader hay columnas, pero totalmente desordenadas. 
	#	Primero hay que decirle en cual columna esta cada variable.
	#	Si types o c1 no estan en el dump o no interesa, asignarles 0
	idscol=0
	typescol=0
	xcol=1
	ycol=2
	c1col=0
	tcol=3
	#	Y la cantidad de columnas hay en total en el dump menos 1 (si hay 6 columnas, Ncols=5)
	Ncols=3

	#	Carpeta en donde se guarda el output. Crear la carpeta antes de correr el script
	folder='output'

	#	Dimensiones del recinto/pasillo
	width=100
	length=100
	door_min=49.08
	door_max=50.92

	#	Para asignarle color a cada type:
	#colores=asigna_colores(types)
	#	Si todos los individuos tienen el mismo color:
	colores='red'
	video_filename='video'
	framerate = 20
	jinicial = 0
	jfinal = 200
	deltaj = 1
	########################################################################

	ids,types,xx,yy,c1,tt,N,M=extract_data(file,idscol,typescol,xcol,ycol,c1col,tcol,Ncols)

	#	El c_1 es para elegir a cuales personas ponerles reborde (por ej los integrantes de los BC
	#	del Dijkstra, que cambia timestep a timestep, o para seguir el comportamiento de un individuo
	#	en particular a lo largo de la simulacion, que seria el mismo c1 para todo timestep)
	c1=np.zeros(N) 
	#	Es nulo si no quiero marcar a ninguno. Si quiero marcar a algunos en particular:
	#	c1[id -1] = 1

	#	j son los timesteps a graficar, se puede elegir j inicial, j final y el delta j
	for j in np.arange(jinicial,jfinal,deltaj):
		plt.clf()
		grafica_timestep_j(j,N,xx,yy,tt,colores,c1,width,length,door_min,door_max)

		pylab.savefig(folder+'/output_%05d.png'%(j), format='png', dpi=100, bbox_inches='tight')

	from_pic_to_vid(video_filename,folder,framerate)

main()
