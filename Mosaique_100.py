from PIL import Image
import math
import os
import sys
def mosaique(chemin_im_source):
	tab_nom_image = os.listdir("base_dimage") 			#acces a notre base de donnee
	im_source_HSV = Image.open(chemin_im_source).convert("HSV") 	#convertit l'image cible en hsv
	new_size =  im_source_HSV.size[0]//100				#taille des petites images
	#on redimensionne l'image cible en fonction de la taille des petites images pour ne pas avoir de demi-image
	im_source_HSV = im_source_HSV.resize(((im_source_HSV.size[0]//new_size)*new_size,(im_source_HSV.size[1]//new_size)*new_size))
	
	cop = im_source_HSV.copy() 	#copie l'image cible en HSV
	pix_copy = cop.load() 		#copy l'image cible pour la modifier
		
	tab = [0]*len(tab_nom_image)
	tab_non_convert = [0]*len(tab_nom_image) 
	

	for i in range(len(tab_nom_image)): #Pour chaque image de la base de donnee
		tab[i] = Image.open("base_dimage/"+tab_nom_image[i]).convert("RGB").convert("HSV") 	#Tableau image base de donnee en HSV
		tab_non_convert[i] = Image.open("base_dimage/"+tab_nom_image[i]).convert("RGB")		#Tableau image base de donnee en RGB

	redimentionne(tab,new_size) #redimentione les images en hsv a la taille new_size
	
	# Creation d'histogramme
	tab_histo = []
	Couleur_Dominante(tab,tab_histo) 
	
	#
	Moyenne_Image_Source(im_source_HSV,new_size,tab_histo,tab,tab_non_convert,pix_copy)
	cop.show()
	cop.convert("RGB").save('Resultat.jpg')
	return cop
 


def redimentionne(tab,new_size): 	#Redimentionnement des images
	for i in range(len(tab)):
		tab[i] = tab[i].resize((new_size,new_size))


def Couleur_Dominante(tab,tab_histo): 	#Creation des histogrammes
	for i in range(len(tab)):
		im = tab[i]		
		histo = im.histogram()
		tab_histo.append((i,histo))


def Moyenne_Image_Source(im_source_HSV,new_size,tab_histo,tab,tab_non_convert,pix_copy): # Moyenne des 25*25 de l'image source
	compte_bug = 0 
	pic_source_25 = Image.new("HSV",(new_size,new_size)) 	# new_size/new_image
	pix_source_25 = pic_source_25.load()			# charge le nouveau carre de 25*25
	pix_source_HSV = im_source_HSV.load()			# charge l'image cible
	for y in range(im_source_HSV.size[1]//new_size):
		for x in range(im_source_HSV.size[0]//new_size):	
			for y_2 in range(new_size):
				for x_2 in range(new_size):	# tout les 25*25
					h,s,v = pix_source_HSV[(new_size*x)+x_2,(new_size*y)+y_2] 	# pour chaque pixel on prend H,S,V
					pix_source_25[x_2,y_2] = h,s,v					# on les remets dans la nouvelle image
			histo_source = pic_source_25.histogram()					# on en prend son histo
			histo_source = [histo_source[:256],histo_source[256:512],histo_source[512:]]	# on le decompose en 3 histo
			indice = Best_Comp(tab_histo,histo_source)					# on garde l'indice de l'image
			
			#pix_tempo = tab_non_convert[indice].load()
			pix_tempo = tab[indice].load()							#charge les pixels de la bonne image
			compte_bug = compte_bug+1							#compteur de petite image faite
			print(compte_bug)
			Remplacement(new_size,pix_copy,pix_tempo,x,y,im_source_HSV.size[0],im_source_HSV.size[1]) # remplace
 


def Best_Comp(tab_histo,histo_source): 	#Recherche de la meilleur image en les comparants dans les carrees de 25*25
	difference_min_h,difference_min_s,difference_min_v = (10**100,)*3	# pixels are in queueleuleu in histo (list)
	indice = 0								# commence a l'indice 0
	diff_min=10**10000							# difference de comparaison min pour trouver la meilleure
	histo_source_nor = norme3(histo_source)					# on normalise 3 histogramme pour l'image source
	for i in range(len(tab_histo)):			#pour chaque histo
		histo_tempo = tab_histo[i][1]				
		histo_tempo = [histo_tempo[:256],histo_tempo[256:512],histo_tempo[512:]] #car 3 histo normalise
		histo_tempo_nor = norme3(histo_tempo)				# on normalise 3 histogramme
		difference_h,difference_s,difference_v = 0,0,0			# pixels are in queueleuleu in histo (list)
		for k in range(len(histo_tempo_nor[0])): 			
			difference_h += abs(histo_tempo_nor[0][k] - histo_source_nor[0][k])*3 	# H
			difference_s += abs(histo_tempo_nor[1][k] - histo_source_nor[1][k]) 	# S
			difference_v += abs(histo_tempo_nor[2][k] - histo_source_nor[2][k]) 	# V

		diff = ((difference_h+1)+(difference_s+1)+(difference_v+1))			# diff HSV

		if diff < diff_min:	#garde le min
			diff_min = diff
			indice = i
	return indice


#Remplacement des 25x25 pixel par la meilleur image
def Remplacement(new_size,pix_copy,pix_tempo,x,y,taille_source_x,taille_source_y):
	for y_2 in range(new_size):
		for x_2 in range(new_size):
			if (new_size*x)+x_2 < taille_source_x and (new_size*y)+y_2 < taille_source_y :
				pix_copy[(new_size*x)+x_2,(new_size*y)+y_2] = pix_tempo[x_2,y_2]

			


			
def norme(histo):			# Norme de un histogramme
	s = sum(histo)
	return [x*(1000/s) for x in histo]
		
def norme3(histo):			# Norme d'un tableau de chaque histogramme
	return [norme(x) for x in histo]		

def main():
    if sys.argv[1] == None:
        print("Vous n'avez pas rentre d'image")
    else :
        mosaique(sys.argv[1])
if __name__ == "__main__":
    
    main()