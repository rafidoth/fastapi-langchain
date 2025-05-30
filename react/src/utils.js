export const getControlMessage = function (control_message) {
  const message = JSON.stringify({
    type: "control",
    event: control_message,
  });
  return message;
};
