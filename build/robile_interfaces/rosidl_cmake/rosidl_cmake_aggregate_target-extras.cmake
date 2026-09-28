# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target robile_interfaces::robile_interfaces
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${robile_interfaces_TARGETS}.
if(robile_interfaces_TARGETS AND NOT TARGET robile_interfaces::robile_interfaces)
  add_library(robile_interfaces::robile_interfaces INTERFACE IMPORTED)
  set_target_properties(robile_interfaces::robile_interfaces PROPERTIES
    INTERFACE_LINK_LIBRARIES "${robile_interfaces_TARGETS}")
endif()
