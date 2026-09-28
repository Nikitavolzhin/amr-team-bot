// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from robile_interfaces:msg/PositionLabelled.idl
// generated code does not contain a copyright notice

#ifndef ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED__TRAITS_HPP_
#define ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "robile_interfaces/msg/detail/position_labelled__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'position'
#include "geometry_msgs/msg/detail/point__traits.hpp"

namespace robile_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const PositionLabelled & msg,
  std::ostream & out)
{
  out << "{";
  // member: name
  {
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << ", ";
  }

  // member: position
  {
    out << "position: ";
    to_flow_style_yaml(msg.position, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PositionLabelled & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << "\n";
  }

  // member: position
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "position:\n";
    to_block_style_yaml(msg.position, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PositionLabelled & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace robile_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use robile_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const robile_interfaces::msg::PositionLabelled & msg,
  std::ostream & out, size_t indentation = 0)
{
  robile_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use robile_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const robile_interfaces::msg::PositionLabelled & msg)
{
  return robile_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<robile_interfaces::msg::PositionLabelled>()
{
  return "robile_interfaces::msg::PositionLabelled";
}

template<>
inline const char * name<robile_interfaces::msg::PositionLabelled>()
{
  return "robile_interfaces/msg/PositionLabelled";
}

template<>
struct has_fixed_size<robile_interfaces::msg::PositionLabelled>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<robile_interfaces::msg::PositionLabelled>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<robile_interfaces::msg::PositionLabelled>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED__TRAITS_HPP_
