# Install script for directory: /home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/aws-robomaker-small-house-world

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/install/aws_robomaker_small_house_world")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world" TYPE DIRECTORY FILES
    "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/aws-robomaker-small-house-world/launch"
    "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/aws-robomaker-small-house-world/models"
    "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/aws-robomaker-small-house-world/worlds"
    "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/aws-robomaker-small-house-world/maps"
    "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/aws-robomaker-small-house-world/photos"
    "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/aws-robomaker-small-house-world/param"
    "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/aws-robomaker-small-house-world/routes"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/package_run_dependencies" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_index/share/ament_index/resource_index/package_run_dependencies/aws_robomaker_small_house_world")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/parent_prefix_path" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_index/share/ament_index/resource_index/parent_prefix_path/aws_robomaker_small_house_world")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world/environment" TYPE FILE FILES "/opt/ros/humble/share/ament_cmake_core/cmake/environment_hooks/environment/ament_prefix_path.sh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world/environment" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_environment_hooks/ament_prefix_path.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world/environment" TYPE FILE FILES "/opt/ros/humble/share/ament_cmake_core/cmake/environment_hooks/environment/path.sh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world/environment" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_environment_hooks/path.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_environment_hooks/local_setup.bash")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_environment_hooks/local_setup.sh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_environment_hooks/local_setup.zsh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_environment_hooks/local_setup.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_environment_hooks/package.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/packages" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_index/share/ament_index/resource_index/packages/aws_robomaker_small_house_world")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world/cmake" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_export_dependencies/ament_cmake_export_dependencies-extras.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world/cmake" TYPE FILE FILES
    "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_core/aws_robomaker_small_house_worldConfig.cmake"
    "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/ament_cmake_core/aws_robomaker_small_house_worldConfig-version.cmake"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/aws_robomaker_small_house_world" TYPE FILE FILES "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/src/aws-robomaker-small-house-world/package.xml")
endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/home/ashraful/HBRS/AMR/AMR_PROJECT/amr-team-bot/build/aws_robomaker_small_house_world/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
