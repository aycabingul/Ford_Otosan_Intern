eimport torch
import torch.nn as nn


def double_conv(in_channels,out_channels,mid_channels=None):#Create a function with 2 parameters named double_conv
    if not mid_channels:
        mid_channels = out_channels
        return nn.Sequential(
        #nn.Sequential allows you to create a neural network by specifying the building blocks (nn.Modules) of that network sequentially.
        
            nn.Conv2d(in_channels, mid_channels, kernel_size=3,padding=1),
        #conv2D is a function of convolution to a 2D data (eg an image).
        #Convolution is a mathematical operator that produces a result when a data string goes through a specific process.
        #Think of convolution as applying a filter to our image.
        #The Conv2D function can perform convolution to a much more complex data structure 
        #(not just a single 2D data but a 2D data set) and some additional options like padding and stride.
        #out_channels (int) - The number of channels generated by the convolution
        #kernel_size = 2-tuple specifying the width and height of the 2D convolution window.
        #kernel_size (int or tuple) - Size of the converting kernel
        #padding (int or tuple, optional) - Zero padding added on both sides of the entry (Default: 0)
        #in_channels 3 channels (color images) is initially 3 for images. It should be 1 for black and white images. Some satellite images should have a 4.
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),#activation function
        #The Non-Linearity layer is usually followed by all the Convolutional layers.
        #This layer is called the activation layer (Activation Layer) because it uses one of the activation functions.
        #A neural network without the activation function will act as a linear regression with limited learning power
        #Relu is chosen if your network is very deep and your processing load is a major problem
        #ReLU Function: The rectified linear unit (RELU) is a nonlinear function.
        #The ReLU function takes the value 0 for negative inputs, while x takes the x value for positive inputs.
        #inplace = True means it will directly change the input without allocating any additional output.
            nn.Conv2d(mid_channels, out_channels, kernel_size=3,padding=1),
            nn.BatchNorm2d(out_channels),
        #Normalizes the input layer by re-centering and rescaling neural networks, a method used to make it faster and more stable
            nn.ReLU(inplace=True),
       
        
    )

class FoInternNet(nn.Module):#A class named FoInternNet was created
    def __init__(self,input_size,n_classes):
        super(FoInternNet, self).__init__()
        self.input_size = input_size
        self.n_classes = n_classes
        
        self.dconv_down1 = double_conv(3, 64)
        self.dconv_down2 = double_conv(64, 128)
        self.dconv_down3 = double_conv(128, 256)
        self.dconv_down4 = double_conv(256, 512)  
        
        #self.dropout=nn.Dropout2d(0.5)
        self.maxpool = nn.MaxPool2d(2)#It takes the maximum of the values in the pixels the filter travels.
        #kernel_size = determines the area to be "pool" on and determines step by step.
        self.upsample = nn.Upsample(scale_factor=2,mode='bilinear', align_corners=True)
        #When we want to increase the image dimensions, we basically expand an image and fill in the "gaps" in the original image's rows and columns.
        #scale_factor: scale factor to sample up or down. A tuple corresponds to scale along x and y.
        #Bilinear: Uses all nearby pixels to calculate the value of the pixel using linear interpolations.
        #align_corners = True, pixels points are considered as a guide. The points in the corners are aligned.
        self.dconv_up3 = double_conv(256 + 512, 256)
        self.dconv_up2 = double_conv(128 + 256, 128)
        self.dconv_up1 = double_conv(128 + 64, 64)
        self.conv_last = nn.Conv2d(64, n_classes, 1)
         
             
    def forward(self, x):
        #print(x.shape)
        conv1 = self.dconv_down1(x)
    
        #print(conv1.shape)
        x = self.maxpool(conv1)
        
        #x=self.dropout(x)
        
        #print("maxpool")
        #print(x.shape)
        
        
        conv2 = self.dconv_down2(x)
    
        #print(conv2.shape)
        x = self.maxpool(conv2)
        #x=self.dropout(x)
        #print("maxpool")
        #print(x.shape)
        
        conv3 = self.dconv_down3(x)
        
        #print(conv3.shape)
        x = self.maxpool(conv3)   
        #x=self.dropout(x)
        #print("maxpool")
        #print(x.shape)
        
        x = self.dconv_down4(x)
        #print(x.shape)
        
        x = self.upsample(x)    
        #print("upsample")
        #print(x.shape)
        x = torch.cat([x, conv3], dim=1)#Combines the given tensor array at the given size 
        #dim: the size in which the tensors are combined
     
    
        #print("cat")
        #print(x.shape)
        x = self.dconv_up3(x)

        #print(x.shape)

        x = self.upsample(x)    
        #print("upsample")
        #print(x.shape)

        x = torch.cat([x, conv2], dim=1)    
        #print("cat")
        #print(x.shape)


        x = self.dconv_up2(x)

        #print(x.shape)
        

        x = self.upsample(x)    
        #print("upsample")
        #print(x.shape)

        x = torch.cat([x, conv1], dim=1)   
        #print("cat")
        #print(x.shape)

        
        x = self.dconv_up1(x)

        #print(x.shape)

        
        x = self.conv_last(x)
        #print(x.shape)

        
        x = nn.Softmax(dim=1)(x)
        #print(x.shape)

        return x
    