
/// Holds exported C API functions
pub mod capi;


pub fn get_domains() -> Vec<String> {
  let mut domains = vec![];
  if cfg!(windows) {
    domains.push("C:\\".to_string());
  }
  else {
    domains.push("/".to_string());
  }
  return domains;
}




