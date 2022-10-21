cmake_minimum_required(VERSION 2.8.9)

project(NephrostomyTutor)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "www.SlicerIGT.org")
set(EXTENSION_CATEGORY "Training")
set(EXTENSION_CONTRIBUTORS "Rebecca Hisey")
set(EXTENSION_DESCRIPTION "Ultrasound-guided nephrostomy training")
set(EXTENSION_ICONURL "")
set(EXTENSION_SCREENSHOTURLS "")
set(EXTENSION_DEPENDS "SlicerIGT")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(UsNeedleTutor)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
