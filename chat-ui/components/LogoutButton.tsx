import { useAuth0 } from '@auth0/auth0-react';
import { IconLogout } from '@tabler/icons-react';

const LogoutButton = () => {
  const { logout } = useAuth0();

  return (
    <button
      onClick={() =>
        logout({ logoutParams: { returnTo: window.location.origin } })
      }
      className="flex-grow rounded flex py-4 px-3 items-center gap-3 transition-colors duration-200 text-white cursor-pointer text-sm hover:bg-gray-700"
    >
      <IconLogout size="1.25em"></IconLogout>
      Log Out
    </button>
  );
};

export default LogoutButton;
