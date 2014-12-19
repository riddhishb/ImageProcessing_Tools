#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>

using namespace cv;
using namespace std;

/*//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
1) Take the dct of the image splitted into 8x8 overlapping windows
2) Extract a K=63 image array for the further computation
3) Compute integral Images for each channel
4) Now compute the moments and local kurtosis and variance for each channel
5) Use the closed form expression to calculate the local noise variance of the window and assign it to the centr pixel
*/ /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


int main( int argc, char** argv )
{
	if( argc != 2){
		cout <<" Usage: display_image ImageToLoadAndDisplay" << endl;
		return -1;
	}
	
	Mat image;
	image = imread(argv[1], CV_LOAD_IMAGE_GRAYSCALE);	// Read the file
	int image_rows = image.rows;
	int image_cols = image.cols;
	imshow("Input",image);

	//////////////////////////////////////////////////////////// Initilization//////////////////////////////////////////////////////////////////////

	Mat image_1 = Mat( image_rows, image_cols, CV_64F);
	image.convertTo(image_1, CV_64F);
	Mat temp1[64];
	Mat temp2[64];
	Mat temp3[64];
	Mat temp4[64];
	Mat integralim1[64]; 
	Mat integralim2[64]; 
	Mat integralim3[64]; 
	Mat integralim4[64];
	Mat sigma_channel[64];
	Mat localnoise_var;
	Mat root_kurt_final;
	Mat kurt_channel[64];
	Mat root_kurt_channel[64];
	double sum_1;
	double sum_2;
	double sum_3;
	double sum_4;
	double mu1;
	double mu2;
	double mu3;
	double mu4;
	double sum_root_kurt = 0;
	double sum_sigma_inverse = 0;
	double sum_sigma_square_inverse = 0;
	double sum_kurt_sigma = 0;
	double root_kurt_final_1;

	for(int i=0;i<64;i++){
		temp1[i] = Mat(image_rows-7,image_cols-7,CV_64F);
		temp2[i] = Mat(image_rows-7,image_cols-7,CV_64F);
		temp3[i] = Mat(image_rows-7,image_cols-7,CV_64F);
		temp4[i] = Mat(image_rows-7,image_cols-7,CV_64F);

		integralim1[i] = Mat( image_rows-7, image_cols-7, CV_64F);
		integralim2[i] = Mat( image_rows-7, image_cols-7, CV_64F);
		integralim3[i] = Mat( image_rows-7, image_cols-7, CV_64F);
		integralim4[i] = Mat( image_rows-7, image_cols-7, CV_64F);
		
		sigma_channel[i] = Mat(image_rows-31,image_cols-31,CV_64F);
		kurt_channel[i] = Mat(image_rows-31,image_cols-31,CV_64F);
		root_kurt_channel[i] = Mat(image_rows-31,image_cols-31,CV_64F);
	}

	//////////////////////////////////////////////DST of 8x8 Overlapping Windows/////////////////////////////////////////////////////////////////////

	for(int i=0;i<image_rows-7;i++){
		for(int j=0;j<image_cols-7;j++){
			Rect slice (j,i,8,8);
			Mat temp_slice = Mat(8,8,CV_64F);
			Mat(image_1,slice).copyTo(temp_slice);
			Mat temp_dct;
			dct(temp_slice,temp_dct);

			for(int k=0;k<8;k++){
				for(int l=0;l<8;l++){
					temp1[(8*k)+l].at<double>(i,j) = temp_dct.at<double>(k,l);
				}
			}
		}
	}
	
	///////////////////////////////////////////////////////////// Integral Image Computation /////////////////////////////////////////////////////////////

	for(int i=1;i<64;i++){
		pow(temp1[i],2,temp2[i]);
		pow(temp1[i],3,temp3[i]);
		pow(temp1[i],4,temp4[i]);
		
		integralim1[i].at<double>(0,0) = temp1[i].at<double>(0,0);
		integralim2[i].at<double>(0,0) = temp2[i].at<double>(0,0);
		integralim3[i].at<double>(0,0) = temp3[i].at<double>(0,0);
		integralim4[i].at<double>(0,0) = temp4[i].at<double>(0,0);
		for(int k=1;k<image_rows;k++){
			integralim1[i].at<double>(k,0) = temp1[i].at<double>(k,0) + integralim1[i].at<double>(k-1,0);
			integralim2[i].at<double>(k,0) = temp2[i].at<double>(k,0) + integralim2[i].at<double>(k-1,0);
			integralim3[i].at<double>(k,0) = temp3[i].at<double>(k,0) + integralim3[i].at<double>(k-1,0);
			integralim4[i].at<double>(k,0) = temp4[i].at<double>(k,0) + integralim4[i].at<double>(k-1,0);	
		}
		for(int k=1;k<image_cols;k++){
			integralim1[i].at<double>(0,k) = temp1[i].at<double>(0,k) + integralim1[i].at<double>(0,k-1);
			integralim2[i].at<double>(0,k) = temp2[i].at<double>(0,k) + integralim2[i].at<double>(0,k-1);
			integralim3[i].at<double>(0,k) = temp3[i].at<double>(0,k) + integralim3[i].at<double>(0,k-1);
			integralim4[i].at<double>(0,k) = temp4[i].at<double>(0,k) + integralim4[i].at<double>(0,k-1);	
		}
		for(int k=1;k<image_rows-7;k++){
			for(int j=1;j<image_cols-7;j++){
				integralim1[i].at<double>(k,j) = temp1[i].at<double>(k,j) + integralim1[i].at<double>(k-1,j) + integralim1[i].at<double>(k,j-1) - integralim1[i].at<double>(k-1,j-1);
				integralim2[i].at<double>(k,j) = temp2[i].at<double>(k,j) + integralim2[i].at<double>(k-1,j) + integralim2[i].at<double>(k,j-1) - integralim2[i].at<double>(k-1,j-1);
				integralim3[i].at<double>(k,j) = temp3[i].at<double>(k,j) + integralim3[i].at<double>(k-1,j) + integralim3[i].at<double>(k,j-1) - integralim3[i].at<double>(k-1,j-1);
				integralim4[i].at<double>(k,j) = temp4[i].at<double>(k,j) + integralim4[i].at<double>(k-1,j) + integralim4[i].at<double>(k,j-1) - integralim4[i].at<double>(k-1,j-1);
			}
		}
	}

	////////////////////////////////////////////////////Moment computation and kurtusis for each channel /////////////////////////////////////////////////////////
	
	for(int k=1;k<64;k++){	
		for(int i=16;i<image_rows-24;i++){
			for(int j=16;j<image_cols-24;j++){
				mu1 = (integralim1[k].at<double>(i+16,j+16) - integralim1[k].at<double>(i+16,j-16) - integralim1[k].at<double>(i-16,j+16) + integralim1[k].at<double>(i-16,j-16))/(64*32);
				mu2 = (integralim2[k].at<double>(i+16,j+16) - integralim2[k].at<double>(i+16,j-16) - integralim2[k].at<double>(i-16,j+16) + integralim2[k].at<double>(i-16,j-16))/(64*32);
				mu3 = (integralim3[k].at<double>(i+16,j+16) - integralim3[k].at<double>(i+16,j-16) - integralim3[k].at<double>(i-16,j+16) + integralim3[k].at<double>(i-16,j-16))/(64*32);
				mu4 = (integralim4[k].at<double>(i+16,j+16) - integralim4[k].at<double>(i+16,j-16) - integralim4[k].at<double>(i-16,j+16) + integralim4[k].at<double>(i-16,j-16))/(64*32);

				sigma_channel[k].at<double>(i,j) = mu2 - (mu1*mu1);
				kurt_channel[k].at<double>(i,j) = ((mu4-(4*mu3*mu1)+(6*mu2*mu1*mu1)-(3*mu1*mu1*mu1*mu1))/((mu2-(mu1*mu1))*(mu2-(mu1*mu1))))-3; //Here
				if(kurt_channel[k].at<double>(i,j) < 0){
					kurt_channel[k].at<double>(i,j) = 0;
				}
			}
		}
	}

	for(int i=1;i<64;i++){
		pow(kurt_channel[i],0.5,root_kurt_channel[i]);
	}
	Mat display;

	///////////////////////////////////////////////////////Computing local kurtosis and Noise Variance ///////////////////////////////////////////////////

	localnoise_var = Mat(kurt_channel[1].rows-1,kurt_channel[1].cols-1,CV_64F);
	root_kurt_final = Mat(kurt_channel[1].rows-1,kurt_channel[1].cols-1,CV_64F);
	for(int i=0;i<kurt_channel[1].rows-1;i++){
		for(int j=0;j<kurt_channel[1].cols-1;j++){
			sum_root_kurt = 0;
			sum_sigma_inverse = 0;
			sum_sigma_square_inverse = 0;
			sum_kurt_sigma = 0;
		for(int k=1;k<64;k++){	
			sum_root_kurt = sum_root_kurt + root_kurt_channel[k].at<double>(i,j);
			sum_sigma_inverse = sum_sigma_inverse + (1/sigma_channel[k].at<double>(i,j));
			sum_sigma_square_inverse = sum_sigma_square_inverse + (1/((sigma_channel[k].at<double>(i,j))*(sigma_channel[k].at<double>(i,j))));
			sum_kurt_sigma = sum_kurt_sigma + ((root_kurt_channel[k].at<double>(i,j))/sigma_channel[k].at<double>(i,j));
		}
		root_kurt_final_1 = (((sum_root_kurt/63)*(sum_sigma_square_inverse/63)) - ((sum_kurt_sigma/63)*(sum_sigma_inverse/63)))/((sum_sigma_square_inverse/63) - ((sum_sigma_inverse/63)*(sum_sigma_inverse/63)));
		localnoise_var.at<double>(i,j) = ((63/sum_sigma_inverse) - ((sum_root_kurt/63)/((sum_sigma_inverse/63)*root_kurt_final_1)));
		}
	}

	for(int i=0;i<kurt_channel[1].rows-1;i++){
		for(int j=0;j<kurt_channel[1].cols-1;j++){
			localnoise_var.at<double>(i,j) = ((localnoise_var.at<double>(i,j)) * 50);
		}
	}

	localnoise_var.convertTo(display, CV_8U);	
	imshow("Spliced Output",display);


	waitKey(0);
}
