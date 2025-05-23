# Install script for directory: /home/ecd508/f1tenth_ws_4/src/f1tenth_system/ackermann_mux

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/ecd508/f1tenth_ws_4/install/ackermann_mux")
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
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/ackermann_mux/ackermann_mux" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/ackermann_mux/ackermann_mux")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/ackermann_mux/ackermann_mux"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/ackermann_mux" TYPE EXECUTABLE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ackermann_mux")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/ackermann_mux/ackermann_mux" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/ackermann_mux/ackermann_mux")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/ackermann_mux/ackermann_mux"
         OLD_RPATH "/home/ecd508/ros2_humble/install/rclcpp/lib:/home/ecd508/ros2_humble/install/libstatistics_collector/lib:/home/ecd508/ros2_humble/install/rcl/lib:/home/ecd508/ros2_humble/install/rmw_implementation/lib:/home/ecd508/ros2_humble/install/ament_index_cpp/lib:/home/ecd508/ros2_humble/install/rcl_logging_spdlog/lib:/home/ecd508/ros2_humble/install/rcl_logging_interface/lib:/home/ecd508/ros2_humble/install/rcl_interfaces/lib:/home/ecd508/ros2_humble/install/rcl_yaml_param_parser/lib:/home/ecd508/ros2_humble/install/libyaml_vendor/lib:/home/ecd508/ros2_humble/install/rosgraph_msgs/lib:/home/ecd508/ros2_humble/install/statistics_msgs/lib:/home/ecd508/ros2_humble/install/tracetools/lib:/home/ecd508/ros2_humble/install/diagnostic_msgs/lib:/home/ecd508/ros2_humble/install/std_msgs/lib:/home/ecd508/ros2_humble/install/builtin_interfaces/lib:/home/ecd508/ros2_humble/install/rosidl_typesupport_fastrtps_c/lib:/home/ecd508/ros2_humble/install/rosidl_typesupport_fastrtps_cpp/lib:/home/ecd508/ros2_humble/install/fastcdr/lib:/home/ecd508/ros2_humble/install/rmw/lib:/home/ecd508/ros2_humble/install/rosidl_typesupport_introspection_cpp/lib:/home/ecd508/ros2_humble/install/rosidl_typesupport_introspection_c/lib:/home/ecd508/ros2_humble/install/rosidl_typesupport_cpp/lib:/home/ecd508/ros2_humble/install/rosidl_typesupport_c/lib:/home/ecd508/ros2_humble/install/rcpputils/lib:/home/ecd508/ros2_humble/install/rosidl_runtime_c/lib:/home/ecd508/ros2_humble/install/rcutils/lib:/opt/ros/humble/lib:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/ackermann_mux/ackermann_mux")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux/launch" TYPE DIRECTORY FILES "/home/ecd508/f1tenth_ws_4/src/f1tenth_system/ackermann_mux/launch/")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux/config" TYPE DIRECTORY FILES "/home/ecd508/f1tenth_ws_4/src/f1tenth_system/ackermann_mux/config/")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE DIRECTORY FILES "/home/ecd508/f1tenth_ws_4/src/f1tenth_system/ackermann_mux/include/")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/package_run_dependencies" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_index/share/ament_index/resource_index/package_run_dependencies/ackermann_mux")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/parent_prefix_path" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_index/share/ament_index/resource_index/parent_prefix_path/ackermann_mux")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux/environment" TYPE FILE FILES "/home/ecd508/ros2_humble/install/ament_cmake_core/share/ament_cmake_core/cmake/environment_hooks/environment/ament_prefix_path.sh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux/environment" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_environment_hooks/ament_prefix_path.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux/environment" TYPE FILE FILES "/home/ecd508/ros2_humble/install/ament_cmake_core/share/ament_cmake_core/cmake/environment_hooks/environment/path.sh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux/environment" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_environment_hooks/path.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_environment_hooks/local_setup.bash")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_environment_hooks/local_setup.sh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_environment_hooks/local_setup.zsh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_environment_hooks/local_setup.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_environment_hooks/package.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/packages" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_index/share/ament_index/resource_index/packages/ackermann_mux")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux/cmake" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_export_include_directories/ament_cmake_export_include_directories-extras.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux/cmake" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_export_dependencies/ament_cmake_export_dependencies-extras.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux/cmake" TYPE FILE FILES
    "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_core/ackermann_muxConfig.cmake"
    "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/ament_cmake_core/ackermann_muxConfig-version.cmake"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ackermann_mux" TYPE FILE FILES "/home/ecd508/f1tenth_ws_4/src/f1tenth_system/ackermann_mux/package.xml")
endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/home/ecd508/f1tenth_ws_4/build/ackermann_mux/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
