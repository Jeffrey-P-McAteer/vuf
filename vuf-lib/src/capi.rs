
use crate::*;

use libc::c_char;

#[no_mangle]
pub extern "C" fn vuf_get_domains_count() -> u32 {
  return get_domains().len() as u32;
}

#[no_mangle]
pub extern "C" fn vuf_get_domain(i: u32, buffer: *mut c_char, buffer_len: u32) {
  // TODO fill buffer w/ item

}



