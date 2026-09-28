// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from robile_interfaces:msg/PositionLabelled.idl
// generated code does not contain a copyright notice

#ifndef ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED__BUILDER_HPP_
#define ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "robile_interfaces/msg/detail/position_labelled__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace robile_interfaces
{

namespace msg
{

namespace builder
{

class Init_PositionLabelled_position
{
public:
  explicit Init_PositionLabelled_position(::robile_interfaces::msg::PositionLabelled & msg)
  : msg_(msg)
  {}
  ::robile_interfaces::msg::PositionLabelled position(::robile_interfaces::msg::PositionLabelled::_position_type arg)
  {
    msg_.position = std::move(arg);
    return std::move(msg_);
  }

private:
  ::robile_interfaces::msg::PositionLabelled msg_;
};

class Init_PositionLabelled_name
{
public:
  Init_PositionLabelled_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PositionLabelled_position name(::robile_interfaces::msg::PositionLabelled::_name_type arg)
  {
    msg_.name = std::move(arg);
    return Init_PositionLabelled_position(msg_);
  }

private:
  ::robile_interfaces::msg::PositionLabelled msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::robile_interfaces::msg::PositionLabelled>()
{
  return robile_interfaces::msg::builder::Init_PositionLabelled_name();
}

}  // namespace robile_interfaces

#endif  // ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED__BUILDER_HPP_
