#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "robile_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__robile_interfaces__msg__PositionLabelled() -> *const std::ffi::c_void;
}

#[link(name = "robile_interfaces__rosidl_generator_c")]
extern "C" {
    fn robile_interfaces__msg__PositionLabelled__init(msg: *mut PositionLabelled) -> bool;
    fn robile_interfaces__msg__PositionLabelled__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<PositionLabelled>, size: usize) -> bool;
    fn robile_interfaces__msg__PositionLabelled__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<PositionLabelled>);
    fn robile_interfaces__msg__PositionLabelled__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<PositionLabelled>, out_seq: *mut rosidl_runtime_rs::Sequence<PositionLabelled>) -> bool;
}

// Corresponds to robile_interfaces__msg__PositionLabelled
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct PositionLabelled {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub position: geometry_msgs::msg::rmw::Point,

}



impl Default for PositionLabelled {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !robile_interfaces__msg__PositionLabelled__init(&mut msg as *mut _) {
        panic!("Call to robile_interfaces__msg__PositionLabelled__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for PositionLabelled {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robile_interfaces__msg__PositionLabelled__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robile_interfaces__msg__PositionLabelled__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robile_interfaces__msg__PositionLabelled__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for PositionLabelled {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for PositionLabelled where Self: Sized {
  const TYPE_NAME: &'static str = "robile_interfaces/msg/PositionLabelled";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__robile_interfaces__msg__PositionLabelled() }
  }
}


#[link(name = "robile_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__robile_interfaces__msg__PositionLabelledArray() -> *const std::ffi::c_void;
}

#[link(name = "robile_interfaces__rosidl_generator_c")]
extern "C" {
    fn robile_interfaces__msg__PositionLabelledArray__init(msg: *mut PositionLabelledArray) -> bool;
    fn robile_interfaces__msg__PositionLabelledArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<PositionLabelledArray>, size: usize) -> bool;
    fn robile_interfaces__msg__PositionLabelledArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<PositionLabelledArray>);
    fn robile_interfaces__msg__PositionLabelledArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<PositionLabelledArray>, out_seq: *mut rosidl_runtime_rs::Sequence<PositionLabelledArray>) -> bool;
}

// Corresponds to robile_interfaces__msg__PositionLabelledArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct PositionLabelledArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub positions: rosidl_runtime_rs::Sequence<super::super::msg::rmw::PositionLabelled>,

}



impl Default for PositionLabelledArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !robile_interfaces__msg__PositionLabelledArray__init(&mut msg as *mut _) {
        panic!("Call to robile_interfaces__msg__PositionLabelledArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for PositionLabelledArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robile_interfaces__msg__PositionLabelledArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robile_interfaces__msg__PositionLabelledArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robile_interfaces__msg__PositionLabelledArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for PositionLabelledArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for PositionLabelledArray where Self: Sized {
  const TYPE_NAME: &'static str = "robile_interfaces/msg/PositionLabelledArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__robile_interfaces__msg__PositionLabelledArray() }
  }
}


