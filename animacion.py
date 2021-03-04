import numpy as np
import math
import random
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import pylab
import os 

def pyparams(fig_size):
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
	          'savefig.dpi': 300,}
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
	#	Nota: el int() no es para redondear, sino porque es molesto que queden como floats.
	#	Quiero un vector Types que sea de longitud N, y corresponda al type de cada persona
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


def grafica_timestep_j(j,N,xx,yy,tt,colores,c1,width,length,door_min,door_max,x_limits,y_limits):
	x=xx[N*j:N*(j+1)]
	y=yy[N*j:N*(j+1)]
	if len(c1)!=N:
		c1=c1[N*j:N*(j+1)] 
	#	Este vector es el c1 en  el timestep j. Si c1 tiene
	#	longitud N es porque es el mismo para todo timestep
	t=tt[N*j]

	fig, ax = plt.subplots()
	circles=[]
	i=0
	for xi,yi in zip(x,y):
		circles+=[ plt.Circle((xi,yi), radius=0.23,color=colores[i], linewidth=3*c1[i],ec='k')]
		i+=1

	c = matplotlib.collections.PatchCollection(circles,match_original=True)
	ax.add_collection(c)
	
	####################### GEOMETRIA #######################
	'''
	xi_obst = 46.32
	xf_obst = 53.68
	yi_obst = 97.7
	yf_obst = 97.7
	wall1 = plt.Rectangle((0,width), door_min, height=0.2,color='k')
	ax.add_patch(wall1)
	wall2 = plt.Rectangle((door_max,width), width, height=0.2,color='k')
	ax.add_patch(wall2)
	panel = plt.Rectangle((xi_obst,yi_obst), width=abs(xf_obst-xi_obst), height=0.2,color='k')
	ax.add_patch(panel)
	'''
	lw=2
	plt.plot([length,length],[0,door_min],'k',lw=lw)
	plt.plot([length,length],[door_max,width],'k',lw=lw)
	
	###################### VISUALES ######################
	ax.set_xlim(x_limits)
	ax.set_ylim(y_limits)
	ax.set_xlabel('x (m)')
	ax.set_ylabel('y (m)')
	ax.set_title('t =%05.2f'%(t))


def from_pic_to_vid(video_filename,output_folder,framerate):
	#	Esta funcion hace un video a partir de la secuencia de imagenes
	comando_para_movie = "ffmpeg -framerate {} -f image2 -pattern_type glob -i '*.png' {}.mp4".format(framerate,video_filename)
	os.system('cd {};{}'.format(output_folder,comando_para_movie))
	#	 y luego borra las imagenes
	os.system('cd {};rm *.png'.format(output_folder))

def main():
	######################## FILE NAMES ######################## 
	file='dump_evac_vd3_eps1.txt'
	video_filename='video_vd3_eps1'
	folder='output_vd3_eps1'
	if not os.path.exists(folder): os.makedirs(folder)

	#	file es un archivo noheader con columnas, pero totalmente desordenadas. 
	#	Las columnas indispensables son time, id, x, y
	#	Primero hay que especificar en cual columna esta cada variable.
	#	Si types o c1 no estan en el dump o no interesa, asignarles 0
	idscol=0
	typescol=1
	xcol=2
	ycol=3
	c1col=4
	tcol=5
	#	Y la cantidad de columnas hay en total en el dump menos 1 (si hay 6 columnas, Ncols=5)
	Ncols=5

	#	Dimensiones del recinto/pasillo
	width=20
	length=20
	door_min=10-0.46
	door_max=10+0.46
	#	Limite a mostrar de los ejes
	x_limits=[15,21]
	y_limits=[7,13]
	#	Dimensiones del del video
	dx = max(x_limits)-min(x_limits)
	dy = max(y_limits)-min(y_limits)
	escala=8
	fig_size =  [escala,escala*dy/dx]
	pyparams(fig_size)

	########################################################################
	ids,types,xx,yy,c1,tt,N,M=extract_data(file,idscol,typescol,xcol,ycol,c1col,tcol,Ncols)

	#	Para asignarle color a cada type:
	#colores=asigna_colores(types)
	#	Si todos los individuos tienen el mismo color:
	colores=N*['red']

	#	El c_1 es para elegir a cuales personas ponerles reborde (por ej los integrantes de los BC
	#	que cambia timestep a timestep, o para seguir el comportamiento de un individuo
	#	en particular a lo largo de la simulacion, que seria el mismo c1 para todo timestep)
	#c1=np.zeros(N) 
	#	Es nulo si no quiero marcar a ninguno. Si quiero marcar a alguno en particular:
	#c1[id_que_quiero -1] = 1

	#	j son los timesteps a graficar, se puede elegir j inicial, j final y el delta j
	framerate = 20
	j_inicial = 1600
	j_final = M
	delta_j = 1
	for j in np.arange(j_inicial,j_final,delta_j):
		plt.close() #Es necesario. Si no van quedando todos los fig,ax de cada timestep abiertos.
		grafica_timestep_j(j,N,xx,yy,tt,colores,c1,width,length,door_min,door_max,x_limits,y_limits)

		pylab.savefig(folder+'/output_%05d.png'%(j), format='png', dpi=100, bbox_inches='tight')

	#from_pic_to_vid(video_filename,folder,framerate)

main()
