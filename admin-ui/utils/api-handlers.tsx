export function getErrorMessageFromResponse(error: any) {
  const { data } = error.response;
  if (typeof data.detail === "string") {
    return data.detail;
  }
  return data.detail[0].msg;
}
