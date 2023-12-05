import { useAuth0 } from "@auth0/auth0-react";
import { IconLogout } from "@tabler/icons-react";
import { Button } from "antd";

const LogoutButton = () => {
  const { logout } = useAuth0();

  return (
    <Button
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
      onClick={() =>
        logout({ logoutParams: { returnTo: window.location.origin } })
      }
    >
      <IconLogout size="1em"></IconLogout>
      Log Out
    </Button>
  );
};

export default LogoutButton;
