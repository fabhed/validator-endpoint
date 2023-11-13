import { useAuth0 } from "@auth0/auth0-react";
import { Button } from "antd";
const LoginButton = () => {
  const { loginWithRedirect } = useAuth0();

  return <Button onClick={() => loginWithRedirect()}>Log In</Button>;
};

export default LoginButton;
