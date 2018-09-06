import numpy as np
import tensorflow as tf
import cv2
import time
import sys
import pdb
import xmltodict
import matplotlib.pyplot as plt
from PIL import Image
import time
import transformation

class YOLO_TF:
	fromfile = None
	tofile_img = 'test/output.jpg'
	tofile_txt = 'test/output.txt'
	imshow = False
	filewrite_img = False
	filewrite_txt = False
	disp_console = True
	weights_file = 'weights/YOLO_tiny.ckpt'
	alpha = 0.1
	threshold = 0.2
	iou_threshold = 0.5
	num_class = 20
	num_box = 2
	grid_size = 7
	classes =  ["aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train","tvmonitor"]

	w_img = 640
	h_img = 480

	def __init__(self,argvs = []):
		self.argv_parser(argvs)
		self.build_networks()
		self.training()
		if self.fromfile is not None and  self.frommuskfile is not None: self.detect_from_file(self.fromfile,self.frommuskfile)#,self.muskfile  and  self.muskfile is not None
	def argv_parser(self,argvs):
		for i in range(1,len(argvs),2):
			# read picture file
			if argvs[i] == '-fromfile' : self.fromfile = argvs[i+1]
			# read muskfile
			if argvs[i] == '-frommuskfile' : self.frommuskfile = argvs[i+1]
			if argvs[i] == '-tofile_img' : self.tofile_img = argvs[i+1] ; self.filewrite_img = True
			if argvs[i] == '-tofile_txt' : self.tofile_txt = argvs[i+1] ; self.filewrite_txt = True
			if argvs[i] == '-imshow' :
				if argvs[i+1] == '1' :self.imshow = True
				else : self.imshow = False
			if argvs[i] == '-disp_console' :
				if argvs[i+1] == '1' :self.disp_console = True
				else : self.disp_console = False
				
	def build_networks(self):
		if self.disp_console : print("Building YOLO_tiny graph...")

		self.sample_matrixes = transformation.target_sample()
		# x is the image
		self.x = tf.placeholder('float32',[1,448,448,3])
		self.musk = tf.placeholder('float32',[1,448,448,3])
		####
		self.punishment = tf.placeholder('float32',[1])
		self.smoothness_punishment=tf.placeholder('float32',[1])
		self.inter = tf.Variable(tf.random_normal([1,448,448,3], stddev=0.001),name='yan')
		# box constraints ensure self.x within(0,1)
		self.w = tf.atanh(self.x)
		# add musk
		self.musked_inter = tf.multiply(self.musk,self.inter)
		self.shuru = tf.add(self.w,self.musked_inter)
		self.constrained = tf.tanh(self.shuru)
		print(self.constrained)

		# for id, sample_matrix in enumerate(self.sample_matrixes):
		# 	if(id >= 2):
		# 		break
		# 	print("sample_matrix type is:", type(sample_matrix))
		# 	tf.contrib.image.transform(self.constrained, sample_matrix)

		tr_image1 = tf.contrib.image.transform(self.constrained, self.sample_matrixes[0])
		tr_image2 = tf.contrib.image.transform(self.constrained, self.sample_matrixes[1])

		tr_image1_back = tf.atanh(tr_image1)
		tr_image2_back = tf.atanh(tr_image2)

		self.sess = tf.Session()
		self.sess.run(tf.global_variables_initializer())
		self.detect_from_file(self.fromfile,self.frommuskfile)
		test_output = self.sess.run([tr_image1, tr_image2, tr_image1_back, tr_image2_back],feed_dict=self.in_dict)#,self.img,self.x,self.tmp0
		# print("tr_image1",test_output[0],"tr_image2",test_output[1], "tr_image1_back", test_output[2], "tr_image2_back", test_output[3])
		
		test_output[0] = (test_output[0] + 1) / 2
		test_output[1] = (test_output[1] + 1) / 2
		print("tr_image1",test_output[0][0],"tr_image2",test_output[1][0])

		img = np.zeros([448,448,3])
		img1 = np.zeros([448,448,3])
		img1[:,:,:] = test_output[0][0]
		img1 = img1.astype(int)
		print(img1[244][244])
		print(img1)
		print("type of test_output[0] is ", type(test_output[0]))
		img[:,:,0] = np.ones([448,448])*64/255.0
		img[:,:,1] = np.ones([448,448])*128/255.0
		img[:,:,2] = np.ones([448,448])*192/255.0
		# img[:,:,0] = test_outputp[0][]
		# img[:,:,1] = np.ones([448,448])*128/255.0
		# img[:,:,2] = np.ones([448,448])*192/255.0

		# output_img1 = cv2.img(test_output[0])

		cv2.namedWindow("output", cv2.WINDOW_NORMAL)

		cv2.imshow('output', img)
		cv2.waitKey()

		cv2.imshow('output', img1)
		cv2.waitKey()

		cv2.imshow('output', test_output[1][0])
		cv2.waitKey()


		# ####
		# self.build_YOLO_model(self.constrained)
		# self.c = tf.reshape(tf.slice(self.fc_19,[0,0],[1,980]),(7,7,20))
		# self.s = tf.reshape(tf.slice(self.fc_19,[0,980],[1,98]),(7,7,2))
		# self.p1 = tf.multiply(self.c[:,:,14],self.s[:,:,0])
		# self.p2 = tf.multiply(self.c[:,:,14],self.s[:,:,1])
		# self.p = tf.stack([self.p1,self.p2],axis=0)
		# self.Cp = tf.reduce_max(self.p) # confidence for people



		# ####################
		# # init an ad example
		# self.perturbation = self.x-self.constrained
		# self.distance_L2 = tf.norm(self.perturbation, ord=2)
		# self.punishment = tf.placeholder('float32',[1])
		# # non-smoothness
		# self.lala1 = self.musked_inter[0:-1,0:-1]
		# self.lala2 = self.musked_inter[1:,1:]
		# self.sub_lala1_2 = self.lala1-self.lala2
		# self.non_smoothness = tf.norm(self.sub_lala1_2, ord=2)
		# # loss is maxpooled confidence + distance_L2 + print smoothness
		# self.loss = self.Cp+self.punishment*self.distance_L2+self.smoothness_punishment*self.non_smoothness
		# # set optimizer
		# self.optimizer = tf.train.AdamOptimizer(1e-2)#GradientDescentOptimizerAdamOptimizer
		# self.attack = self.optimizer.minimize(self.loss,var_list=[self.inter])#,var_list=[self.adversary]
		# ####################
		# self.sess = tf.Session()
		# self.sess.run(tf.global_variables_initializer())
		# #pdb.set_trace()
		# #print(tf.contrib.framework.get_variables())
		# saver = tf.train.Saver(tf.contrib.framework.get_variables()[1:-4])#[0:-1][1:-4]
		# saver.restore(self.sess,self.weights_file)
		
		# if self.disp_console : print("Loading complete!" + '\n')
		
	def build_YOLO_model(self, image):
		self.conv_1 = self.conv_layer(1,image,16,3,1)
		self.pool_2 = self.pooling_layer(2,self.conv_1,2,2)
		self.conv_3 = self.conv_layer(3,self.pool_2,32,3,1)
		self.pool_4 = self.pooling_layer(4,self.conv_3,2,2)
		self.conv_5 = self.conv_layer(5,self.pool_4,64,3,1)
		self.pool_6 = self.pooling_layer(6,self.conv_5,2,2)
		self.conv_7 = self.conv_layer(7,self.pool_6,128,3,1)
		self.pool_8 = self.pooling_layer(8,self.conv_7,2,2)
		self.conv_9 = self.conv_layer(9,self.pool_8,256,3,1)
		self.pool_10 = self.pooling_layer(10,self.conv_9,2,2)
		self.conv_11 = self.conv_layer(11,self.pool_10,512,3,1)
		self.pool_12 = self.pooling_layer(12,self.conv_11,2,2)
		self.conv_13 = self.conv_layer(13,self.pool_12,1024,3,1)
		self.conv_14 = self.conv_layer(14,self.conv_13,1024,3,1)
		self.conv_15 = self.conv_layer(15,self.conv_14,1024,3,1)
		self.fc_16 = self.fc_layer(16,self.conv_15,256,flat=True,linear=False)
		self.fc_17 = self.fc_layer(17,self.fc_16,4096,flat=False,linear=False)
		#skip dropout_18
		self.fc_19 = self.fc_layer(19,self.fc_17,1470,flat=False,linear=True)
        
	def detect_from_cvmat(self,img,musk):
		s = time.time()
		self.h_img,self.w_img,_ = img.shape
		img_resized = cv2.resize(img, (448, 448))
		musk_resized = cv2.resize(musk,(448,448))
		img_RGB = cv2.cvtColor(img_resized,cv2.COLOR_BGR2RGB)
		img_resized_np = np.asarray( img_RGB )
		inputs = np.zeros((1,448,448,3),dtype='float32')
		inputs_musk = np.zeros((1,448,448,3),dtype='float32')
		inputs[0] = (img_resized_np/255.0)*2.0-1.0
		inputs_musk[0] = musk_resized
		# image in numpy format
		self.inputs = inputs
		# hyperparameter to control two optimization objectives
		punishment = np.array([0.0])
		smoothness_punishment = np.array([0.5])
		# search step for a single attack
		steps = 100
		# set original image and punishment
		self.in_dict = {self.x: inputs,
		self.punishment:punishment,
		self.musk:inputs_musk,
		self.smoothness_punishment:smoothness_punishment
		}#,self.img:inputs
		# # attack
		# print("YOLO attack...")
		# for i in range(steps):
		# 	# fetch something in self(tf.Variable)
		# 	net_output = self.sess.run([self.fc_19,self.attack,self.constrained,self.Cp,self.loss],feed_dict=in_dict)#,self.img,self.x,self.tmp0
		# 	print("step:",i,"Confidence:",net_output[3],"Loss:",net_output[4])
		# #pdb.set_trace()
		# #########
		# #print(net_output[1],net_output[2],net_output[3])#,net_output[2],net_output[3],net_output[4]
		# self.result = self.interpret_output(net_output[0][0])
		# ###
		# # reconstruct image from perturbation
		# ad_x=net_output[2]
		# ad_x_01=(ad_x/2.0)+0.5
		# #print(ad_x_01)
		# ###
		# '''
		# fig = plt.figure()
		# bx = fig.add_subplot(111)
		# '''
		# # bx.imshow only take value between 0 and 1
		# squeezed=np.squeeze(ad_x_01)
		# #print(squeezed.max())
		# '''
		# print("Adversarial result:")
		# bx.imshow(squeezed)
		# plt.show()
		# '''
		# ad_x_squeezed=np.squeeze(ad_x)
		# reconstruct_img_resized_np=(ad_x_squeezed+1.0)/2.0*255.0
		# print("min and max in img(numpy form):",reconstruct_img_resized_np.min(),reconstruct_img_resized_np.max())
		
		# reconstruct_img_BGR= cv2.cvtColor(reconstruct_img_resized_np,cv2.COLOR_RGB2BGRA)
		# reconstruct_img_np=cv2.resize(reconstruct_img_BGR,(self.w_img,self.h_img))#reconstruct_img_BGR
		# reconstruct_img_np_squeezed=np.squeeze(reconstruct_img_np)
		
		# savedname=time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+".jpg"
		
		# #pdb.set_trace()
		# path = r"/home/baidu/Program/Jay/YOLO_attack-1/result/"
		# is_saved=cv2.imwrite(path+savedname,reconstruct_img_np_squeezed)
		# if is_saved:
		# 	print("Saved under: ",path+savedname)
		# else:
		# 	print("Saving error!")

		# print("Attack finished!")
		# self.show_results(img ,self.result)
		# strtime = str(time.time()-s)
		# if self.disp_console : print('Elapsed time : ' + strtime + ' secs' + '\n')

	# generate Musk
	def generate_Musk(self,musk, xmin,ymin,xmax,ymax):
		for i in range(xmin,xmax):
			for j in range(ymin,ymax):
				for channel in range(3):
					musk[j][i][channel] = 1
		return musk
		
	def detect_from_file(self,filename,muskfilename):#,muskfilename
		if self.disp_console : print('Detect from ' + filename)
		img = cv2.imread(filename)
		#img = misc.imread(filename)
		f = open(muskfilename)
		pic = plt.imread(filename)
		dic = xmltodict.parse(f.read())
		#str = json.dumps(dic)

		print("Input picture size:",dic['annotation']['size'])
		#shape = [int(dic['annotation']['size']['height']),int(dic['annotation']['size']['width'])]
		print(type(img),img.shape)
		musk = 0.000001*np.ones(shape=img.shape)
		#print(pic)
		print("Generating Musk...")
		for _object in dic['annotation']['object']:
			xmin = int(_object['bndbox']['xmin'])
			ymin = int(_object['bndbox']['ymin'])
			xmax = int(_object['bndbox']['xmax'])
			ymax = int(_object['bndbox']['ymax'])
			print(xmin,ymin,xmax,ymax)
			musk = self.generate_Musk(musk,xmin,ymin,xmax,ymax)
		'''
		fig = plt.figure()
		ax = fig.add_subplot(211)
		ax.imshow(musk)
		bx = fig.add_subplot(212)
		bx.imshow(np.asarray(pic))
		plt.show()  
		'''
		self.detect_from_cvmat(img,musk)

	def conv_layer(self,idx,inputs,filters,size,stride):
		channels = inputs.get_shape()[3]
		weight = tf.Variable(tf.truncated_normal([size,size,int(channels),filters], stddev=0.1))
		biases = tf.Variable(tf.constant(0.1, shape=[filters]))

		pad_size = size//2
		pad_mat = np.array([[0,0],[pad_size,pad_size],[pad_size,pad_size],[0,0]])
		inputs_pad = tf.pad(inputs,pad_mat)

		conv = tf.nn.conv2d(inputs_pad, weight, strides=[1, stride, stride, 1], padding='VALID',name=str(idx)+'_conv')	
		conv_biased = tf.add(conv,biases,name=str(idx)+'_conv_biased')	
		if self.disp_console : print('    Layer  %d : Type = Conv, Size = %d * %d, Stride = %d, Filters = %d, Input channels = %d' % (idx,size,size,stride,filters,int(channels)))
		return tf.maximum(self.alpha*conv_biased,conv_biased,name=str(idx)+'_leaky_relu')

	def pooling_layer(self,idx,inputs,size,stride):
		if self.disp_console : print('    Layer  %d : Type = Pool, Size = %d * %d, Stride = %d' % (idx,size,size,stride))
		return tf.nn.max_pool(inputs, ksize=[1, size, size, 1],strides=[1, stride, stride, 1], padding='SAME',name=str(idx)+'_pool')

	def fc_layer(self,idx,inputs,hiddens,flat = False,linear = False):
		input_shape = inputs.get_shape().as_list()		
		if flat:
			dim = input_shape[1]*input_shape[2]*input_shape[3]
			inputs_transposed = tf.transpose(inputs,(0,3,1,2))
			inputs_processed = tf.reshape(inputs_transposed, [-1,dim])
		else:
			dim = input_shape[1]
			inputs_processed = inputs
		weight = tf.Variable(tf.truncated_normal([dim,hiddens], stddev=0.1))
		biases = tf.Variable(tf.constant(0.1, shape=[hiddens]))	
		if self.disp_console : print('    Layer  %d : Type = Full, Hidden = %d, Input dimension = %d, Flat = %d, Activation = %d' % (idx,hiddens,int(dim),int(flat),1-int(linear))	)
		if linear : return tf.add(tf.matmul(inputs_processed,weight),biases,name=str(idx)+'_fc')
		ip = tf.add(tf.matmul(inputs_processed,weight),biases)
		return tf.maximum(self.alpha*ip,ip,name=str(idx)+'_fc')

	def detect_from_crop_sample(self):
		self.w_img = 640
		self.h_img = 420
		f = np.array(open('person_crop.txt','r').readlines(),dtype='float32')
		inputs = np.zeros((1,448,448,3),dtype='float32')
		for c in range(3):
			for y in range(448):
				for x in range(448):
					inputs[0,y,x,c] = f[c*448*448+y*448+x]

		in_dict = {self.x: inputs}
		net_output = self.sess.run(self.fc_19,feed_dict=in_dict)
		self.boxes, self.probs = self.interpret_output(net_output[0])
		img = cv2.imread('person.jpg')
		self.show_results(self.boxes,img)

	def interpret_output(self,output):
		probs = np.zeros((7,7,2,20))
		class_probs = np.reshape(output[0:980],(7,7,20))
		scales = np.reshape(output[980:1078],(7,7,2))
		boxes = np.reshape(output[1078:],(7,7,2,4))
		offset = np.transpose(np.reshape(np.array([np.arange(7)]*14),(2,7,7)),(1,2,0))
		debug_yan=np.zeros((7,7,2))
		for i in range(2):
			debug_yan[:,:,i]=np.multiply(class_probs[:,:,14],scales[:,:,i])
		#print(debug_yan.reshape(-1))
		boxes[:,:,:,0] += offset
		boxes[:,:,:,1] += np.transpose(offset,(1,0,2))
		boxes[:,:,:,0:2] = boxes[:,:,:,0:2] / 7.0
		boxes[:,:,:,2] = np.multiply(boxes[:,:,:,2],boxes[:,:,:,2])
		boxes[:,:,:,3] = np.multiply(boxes[:,:,:,3],boxes[:,:,:,3])
		
		boxes[:,:,:,0] *= self.w_img
		boxes[:,:,:,1] *= self.h_img
		boxes[:,:,:,2] *= self.w_img
		boxes[:,:,:,3] *= self.h_img

		for i in range(2):
			for j in range(20):
				probs[:,:,i,j] = np.multiply(class_probs[:,:,j],scales[:,:,i])
		#print probs
		filter_mat_probs = np.array(probs>=self.threshold,dtype='bool')
		filter_mat_boxes = np.nonzero(filter_mat_probs)
		
		boxes_filtered = boxes[filter_mat_boxes[0],filter_mat_boxes[1],filter_mat_boxes[2]]
		probs_filtered = probs[filter_mat_probs]

		classes_num_filtered = np.argmax(filter_mat_probs,axis=3)[filter_mat_boxes[0],filter_mat_boxes[1],filter_mat_boxes[2]] 

		argsort = np.array(np.argsort(probs_filtered))[::-1]
		boxes_filtered = boxes_filtered[argsort]
		probs_filtered = probs_filtered[argsort]
		classes_num_filtered = classes_num_filtered[argsort]
		
		for i in range(len(boxes_filtered)):
			if probs_filtered[i] == 0 : continue
			for j in range(i+1,len(boxes_filtered)):
				if self.iou(boxes_filtered[i],boxes_filtered[j]) > self.iou_threshold : 
					probs_filtered[j] = 0.0
		
		filter_iou = np.array(probs_filtered>0.0,dtype='bool')
		boxes_filtered = boxes_filtered[filter_iou]
		probs_filtered = probs_filtered[filter_iou]
		
		
		#pdb.set_trace()
		classes_num_filtered = classes_num_filtered[filter_iou]

		result = []
		for i in range(len(boxes_filtered)):
			result.append([self.classes[classes_num_filtered[i]],boxes_filtered[i][0],boxes_filtered[i][1],boxes_filtered[i][2],boxes_filtered[i][3],probs_filtered[i]])

		return result

	def show_results(self,img,results):
		img_cp = img.copy()
		if self.filewrite_txt :
			ftxt = open(self.tofile_txt,'w')
		for i in range(len(results)):
			x = int(results[i][1])
			y = int(results[i][2])
			w = int(results[i][3])//2
			h = int(results[i][4])//2
			if self.disp_console : print('    class : ' + results[i][0] + ' , [x,y,w,h]=[' + str(x) + ',' + str(y) + ',' + str(int(results[i][3])) + ',' + str(int(results[i][4]))+'], Confidence = ' + str(results[i][5]))
			if self.filewrite_img or self.imshow:
				cv2.rectangle(img_cp,(x-w,y-h),(x+w,y+h),(0,255,0),2)
				cv2.rectangle(img_cp,(x-w,y-h-20),(x+w,y-h),(125,125,125),-1)
				cv2.putText(img_cp,results[i][0] + ' : %.2f' % results[i][5],(x-w+5,y-h-7),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1)
			if self.filewrite_txt :				
				ftxt.write(results[i][0] + ',' + str(x) + ',' + str(y) + ',' + str(w) + ',' + str(h)+',' + str(results[i][5]) + '\n')
		if self.filewrite_img : 
			if self.disp_console : print('    image file writed : ' + self.tofile_img)
			cv2.imwrite(self.tofile_img,img_cp)			
		if self.imshow :
			cv2.imshow('YOLO_tiny detection',img_cp)
			cv2.waitKey(1)
		if self.filewrite_txt : 
			if self.disp_console : print('    txt file writed : ' + self.tofile_txt)
			ftxt.close()

	def iou(self,box1,box2):
		tb = min(box1[0]+0.5*box1[2],box2[0]+0.5*box2[2])-max(box1[0]-0.5*box1[2],box2[0]-0.5*box2[2])
		lr = min(box1[1]+0.5*box1[3],box2[1]+0.5*box2[3])-max(box1[1]-0.5*box1[3],box2[1]-0.5*box2[3])
		if tb < 0 or lr < 0 : intersection = 0
		else : intersection =  tb*lr
		return intersection / (box1[2]*box1[3] + box2[2]*box2[3] - intersection)
		
	def readimage(self, filename):
		if self.disp_console : print('Detect from ' + filename)
		img = cv2.imread(filename)
		#img = misc.imread(filename)
		s = time.time()
		self.h_img,self.w_img,_ = img.shape
		img_resized = cv2.resize(img, (448, 448))
		img_RGB = cv2.cvtColor(img_resized,cv2.COLOR_BGR2RGB)
		img_resized_np = np.asarray( img_RGB )
		inputs = np.zeros((1,448,448,3),dtype='float32')
		inputs[0] = (img_resized_np/255.0)*2.0-1.0
		self.inputs = inputs
	
	def training(self): #TODO add training function!
		
		return None
	
	
			

def main(argvs):
	yolo = YOLO_TF(argvs)
	#cv2.waitKey(5000)


if __name__=='__main__':	
	main(sys.argv)
