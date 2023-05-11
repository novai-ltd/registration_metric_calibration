import SimpleITK as sitk
from skimage.metrics import normalized_mutual_information
from skimage.color import rgb2gray

def calculate_metrics(image_1, image_2):

    return normalized_mutual_information(image_1, image_2), normalized_cross_correlation(image_1, image_2), mean_squares(image_1, image_2)

def normalized_cross_correlation(image_1, image_2) :

    # initialize registration to give access to metric
    corr = sitk.ImageRegistrationMethod()
    corr.SetMetricAsCorrelation()
    corr.SetInitialTransform(sitk.Transform(2, sitk.sitkIdentity))

    # convert images
    image_1 = sitk.GetImageFromArray(image_1)
    image_2 = sitk.GetImageFromArray(image_2)
    image_1 = sitk.Cast(image_1, sitk.sitkFloat32)
    image_2 = sitk.Cast(image_2, sitk.sitkFloat32)
    image_1.SetSpacing((1, 1))
    image_2.SetSpacing((1, 1))

    # calculate metric
    return corr.MetricEvaluate(image_1, image_2)

def mean_squares(image_1, image_2) :

    # initialize registration to give access to metric
    corr = sitk.ImageRegistrationMethod()
    corr.SetMetricAsMeanSquares()
    corr.SetInitialTransform(sitk.Transform(2, sitk.sitkIdentity))

    # convert images
    image_1 = sitk.GetImageFromArray(image_1)
    image_2 = sitk.GetImageFromArray(image_2)
    image_1 = sitk.Cast(image_1, sitk.sitkFloat32)
    image_2 = sitk.Cast(image_2, sitk.sitkFloat32)

    # calculate metric
    return corr.MetricEvaluate(image_1, image_2)