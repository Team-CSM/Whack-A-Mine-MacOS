from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
import os, subprocess
import sys, image_slicer
from PIL import Image
import numpy as np
from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from keras.models import Sequential, load_model


###################################################### To get relative path when built 

if getattr(sys, 'frozen', False): # when built
    application_path = os.path.dirname(sys.executable)
    application_path = application_path[:application_path.rfind('/')]
    application_path = application_path[:application_path.rfind('/')]

elif __file__: # when developing
	application_path = os.path.dirname(__file__)

###################################################### Variables needed for launcher

IMAGES_DICT = {} # { imageName: [path, owner]} # owner = players/creator/selects
LOGFILEPATH = os.path.join(application_path, "logfile.txt")
CLASSNAMES = ["burns", "cloud", "mines"]
FONTBTN="Futura 12 bold"
FONTLABEL="Futura 12 bold"
CURSORBTN = "center_ptr"

############################################################ Variables needed when predicting
img_width, img_height = 64, 64
model_path = os.path.join(application_path, 'model.h5')
model_weights_path = os.path.join(application_path, 'weights.h5')
model = load_model(model_path)
model.load_weights(model_weights_path)
class_to_name = ["clear", "cloudy", "mine", "slash"]

######################################################################################
def main(imgPathe):

	imgPath = imgPathe # python predictMulti.py ./players_money/orig.jpg
	dirPath = imgPath[:imgPath.rfind('/')+1]
	IMAGE = imgPath
	locationSlices = dirPath + 'slices'

	if not os.path.exists(locationSlices):
		os.makedirs(locationSlices)
		slice(900, IMAGE, locationSlices)

	imgstr = []

	# Add all slices to the imgstr
	for root, dirs, filenames in os.walk(locationSlices):
		for f in filenames:
			if (f.startswith('.') == False):
				imgstr.append(locationSlices + '/' + f)

	# Getting predictions for all the slices from the model
	predict(imgstr, class_to_name, dirPath)

	# Finally splitting the input image into 9 slices, with set ratio to be input to game.
	slice(9, IMAGE, dirPath)

    # print("resizing...")
	for root, dirs, filenames in os.walk(dirPath):
		for f in filenames:
			if f[-3:]==".png":
				im = Image.open(dirPath + f)
				nx, ny = im.size
				im = im.resize((int(nx*1.4), ny), Image.BICUBIC)
				im.save(dirPath + f)
    
	subprocess.call(["rm","-r",locationSlices]) #cleanup= delete the thousands of slices

def slice(number, IMAGE, location):
    # slice image for stream and add to the slices folder
    
    print("slicing...")
    tiles = image_slicer.slice(IMAGE, number, save=False)
    image_slicer.save_tiles(tiles, directory=location, prefix='slice')


def predict(imgstr, class_to_name, dirPath):
    print("predicting...")
    for image in imgstr:
        x = load_img(image, target_size=(img_width,img_height))
        
        x = img_to_array(x)
        x = np.expand_dims(x, axis=0)
        x = x/255 # normalise
        
        
        predictions = model.predict(x) #predictions in each class
        pred = np.argmax(predictions[0]) #winner index
        
        if (max(predictions[0]) > 0.5):
            out1 = class_to_name[pred]
            
            #write coordinates to log files to help out with input to game
            f = open(dirPath+out1+".txt", "a")
            f.write(image[image.rfind('/')+7:-4].replace("_", ",") + "_")
            f.close()


######################################################################################
def launchGame():

	gamePath = os.path.join(application_path, "GameMac.app")
	subprocess.call(["open", gamePath])
	root.destroy()

######################################################################################
def getImage(imgPath):
	img = Image.open(imgPath).resize((165, 165), Image.ANTIALIAS)
	img = ImageTk.PhotoImage(img)
	return img
######################################################################################
def updateLsbox():

	if (application_path == ""):
		toWalk = "./"
	else:
		toWalk = application_path + "/"

	lsbox.delete(0, END)
	IMAGES_DICT.clear()

	for dirname, dirnames, filenames in os.walk(toWalk):
		if (dirname[:len(toWalk)+8]==toWalk+"players_" or dirname[:len(toWalk)+8]==toWalk+"creator_"):
			imageName = dirname[dirname.rfind('_')+1:]
			path = dirname+'/'
			owner = dirname[dirname.rfind('_')-7:dirname.rfind('_')]
			IMAGES_DICT[imageName] = [path, owner]
			lsbox.insert(END,imageName)

######################################################################################

def browse():
	source = askopenfilename(initialdir = "/", title = "Select file",
								filetypes = (("jpeg files","*.jpg"),
												("GIF files","*.gif"),
												("PNG files","*.png")))
	uploadPathVar.set(source)


######################################################################################
def upload():

	uploadPathEntryText = uploadPathEntry.get()
	uploadNameEntryText = uploadNameEntry.get()


	if (uploadPathEntryText == "") or (uploadNameEntryText == ""):
		popup("Must specify path and name of image to upload.")
		return
	if uploadNameEntryText in IMAGES_DICT:
		popup("Image name already exists. Change name of image to rename it to.")
		return
	if "_" in uploadNameEntryText:
		popup("Name of image must not include underscores (_)")
		return
		
	imgOrigFileName = uploadPathEntryText[uploadPathEntryText.rfind("/")+1:]
	newDir = os.path.join(application_path, "./players_"+uploadNameEntryText)

	if not os.path.exists(newDir):
		os.makedirs(newDir)

	subprocess.call(["cp", uploadPathEntryText, newDir])
	beforePathName = newDir+'/'+imgOrigFileName
	afterPathName = newDir+"/orig"
	subprocess.call(["mv", beforePathName, afterPathName+".jpg"])

	afterPathName = afterPathName+".jpg"
	main(afterPathName)

	updateLsbox()

######################################################################################
def view():
	selection = lsbox.curselection()
	if (len(selection) == 0):
		popup("No item selected.")
		return	
	imgNameSelected = lsbox.get(selection[0])
	imgActivePath = IMAGES_DICT[imgNameSelected][0]

	img = getImage(imgActivePath+"orig.jpg")
	myvar = Label(selectedLab, image = img)
	myvar.image = img
	myvar.grid(row=0, column=0)
######################################################################################
def delete():

	selection = lsbox.curselection()

	if (len(selection) == 0):
		popup("No item selected.")
		return

	imgNameSelected = lsbox.get(selection[0])
	imgSelectedPath = IMAGES_DICT[imgNameSelected][0]
	ownerImg = IMAGES_DICT[imgNameSelected][1]

	if (ownerImg == "creator"):
		popup("Cannot delete creators' images. You can only delete images you uploaded.")
		return

	subprocess.call(["rm","-r",imgSelectedPath])

	updateLsbox()

######################################################################################

def select():

	selection = lsbox.curselection()

	if (len(selection) == 0):
		popup("No item selected.")
		return

	imgNameSelected = lsbox.get(selection[0])
	imgSelectedPath = IMAGES_DICT[imgNameSelected][0]        		

	file = open(LOGFILEPATH, "w")
	file.write(imgSelectedPath)
	file.close()

	launchGame()
######################################################################################
def rename():

	selection = lsbox.curselection()
	renameEntryText = renameEntry.get()


	if len(selection) == 0 or renameEntryText == "":
		popup("Must select item and specify name to rename image to.")
		return

	if renameEntryText in IMAGES_DICT:
		popup("Image name already exists. Change name of image to rename it to.")
		return

	if "_" in renameEntryText:
		popup("Name of image must not include underscores (_)")
		return

	imgNameSelected = lsbox.get(selection[0])
	imgSelectedPath = IMAGES_DICT[imgNameSelected][0]
	ownerImg = IMAGES_DICT[imgNameSelected][1]

	if (ownerImg == "creator"):
		popup("Cannot rename creators' images. You can only rename images you uploaded.")
		return

	beforePath = imgSelectedPath
	afterPath = imgSelectedPath[:imgSelectedPath.rfind('_')+1]+renameEntryText

	subprocess.call(["mv", beforePath, afterPath])
	updateLsbox()
######################################################################################
def popup(msg):
	messagebox.showinfo("Alert", msg)

######################################################################################

root = Tk()

root.title("Whack-A-Mine")
root.resizable(False,False)


heading = Label(root, text="Whack-A-Mine\n(Select image to play)", font = "Futura 24 bold")
heading.grid(row=0, columnspan=3, sticky="we")
heading.configure(background='pale green')

frameUpload = Frame(root)
frameUpload.grid(row=1, columnspan=3, sticky="nsew")
frameUpload.grid_rowconfigure(0, weight=1)
frameUpload.grid_columnconfigure(0, weight=1)


uploadLabel = Label(frameUpload, text="Upload your own image", font=FONTLABEL).grid(row=0, columnspan=3, sticky=NSEW)
uploadNameLabel = Label(frameUpload, text="Name", font=FONTLABEL).grid(row=1, column=0)
uploadPathLabel = Label(frameUpload, text="Path", font=FONTLABEL).grid(row=2, column=0)


uploadNameEntry = Entry(frameUpload, width=50, relief=RIDGE)
uploadPathVar = StringVar()
uploadPathEntry = Entry(frameUpload, textvariable=uploadPathVar, width=50, relief=RIDGE)

browseBtn = Button(frameUpload, text="Browse", command=browse, font=FONTBTN, cursor=CURSORBTN, bg="green")
uploadBtn = Button(frameUpload, text="Upload", command=upload, font=FONTBTN, cursor=CURSORBTN)

uploadNameEntry.grid(row=1, column=1, sticky=W)
uploadPathEntry.grid(row=2, column=1, sticky=W)

browseBtn.grid(row=2, column=2, sticky=E)
uploadBtn.grid(row=3, columnspan=3, sticky=NSEW)


frameList = Frame(root)
frameList.grid(row=2, column=0)

lsbox = Listbox(frameList)#, width=25, height=25)
scrollbar = Scrollbar(frameList, orient="vertical")
lsbox.config(background='pale green')
scrollbar.config(command=lsbox.yview)
lsbox.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
lsbox.pack(side="left", fill="y")
lsbox.selection_set(first=0)


frameBtns = Frame(root)
frameBtns.grid(row=2, column=1)

viewBtn = Button(frameBtns, text="View", command=view, font=FONTBTN, cursor=CURSORBTN).pack()
selectBtn = Button(frameBtns, text="Select", command=select, font=FONTBTN, cursor=CURSORBTN).pack()
deleteBtn = Button(frameBtns, text="Delete", command=delete, font=FONTBTN, cursor=CURSORBTN).pack()

renameLabel = Label(frameBtns, text="Rename:", font=FONTLABEL)
renameEntry = Entry(frameBtns, relief=RIDGE)
renameBtn = Button(frameBtns, text="Rename", command=rename, font=FONTBTN, cursor=CURSORBTN)
renameLabel.pack()
renameEntry.pack()
renameBtn.pack()

selectedLab = Label(root, width=20, height=10, text="Select image to view here")
selectedLab.grid(row=2, column=2)
selectedLab.configure(background='pale green')

updateLsbox()


root.mainloop()

