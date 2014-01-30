#ifndef CONFIG_H
#define CONFIG_H

#include "Precision.h"

#include "itkImage.h"

#include "ImageVectorConverter.h"


#include "itkRGBPixel.h"


typedef itk::Image<Precision, DIMENSION> Image;

typedef itk::Image< itk::RGBPixel<Precision>, DIMENSION> ColorImage;



#endif
