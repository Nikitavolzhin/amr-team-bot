// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from robile_interfaces:msg/PositionLabelledArray.idl
// generated code does not contain a copyright notice

#ifndef ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__TRAITS_HPP_
#define ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "robile_interfaces/msg/detail/position_labelled_array__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'positions'
#include "robile_interfaces/msg/detail/position_labelled__traits.hpp"

namespace robile_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const PositionLabelledArray & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: positions
  {
    if (msg.positions.size() == 0) {
      out << "positions: []";
    } else {
      out << "positions: [";
      size_t pending_items = msg.positions.size();
      for (auto item : msg.positions) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PositionLabelledArray & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: positions
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.positions.size() == 0) {
      out << "positions: []\n";
    } else {
      out << "positions:\n";
      for (auto item : msg.positions) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PositionLabelledArray & msg, bool use_flow_style = false)
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
  const robile_interfaces::msg::PositionLabelledArray & msg,
  std::ostream & out, size_t indentation = 0)
{
  robile_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use robile_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const robile_interfaces::msg::PositionLabelledArray & msg)
{
  return robile_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<robile_interfaces::msg::PositionLabelledArray>()
{
  return "robile_interfaces::msg::PositionLabelledArray";
}

template<>
inline const char * name<robile_interfaces::msg::PositionLabelledArray>()
{
  return "robile_interfaces/msg/PositionLabelledArray";
}

template<>
struct has_fixed_size<robile_interfaces::msg::PositionLabelledArray>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<robile_interfaces::msg::PositionLabelledArray>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<robile_interfaces::msg::PositionLabelledArray>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__TRAITS_HPP_
