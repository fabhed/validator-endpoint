import { useAuth0 } from '@auth0/auth0-react';
import { IconDots, IconFileExport, IconSettings } from '@tabler/icons-react';
import { useContext, useEffect, useRef, useState } from 'react';

import { useTranslation } from 'next-i18next';

import HomeContext from '@/pages/api/home/home.context';

import LogoutButton from '@/components/LogoutButton';
import { SettingDialog } from '@/components/Settings/SettingDialog';

import { Import } from '../../Settings/Import';
import { SidebarButton } from '../../Sidebar/SidebarButton';
import ChatbarContext from '../Chatbar.context';
import { ClearConversations } from './ClearConversations';

export const ChatbarSettings = () => {
  const { user, isAuthenticated, isLoading } = useAuth0();

  const { t } = useTranslation('sidebar');
  const [isSettingDialogOpen, setIsSettingDialog] = useState<boolean>(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] =
    useState<boolean>(false);

  const {
    state: { conversations },
    dispatch: homeDispatch,
  } = useContext(HomeContext);

  const {
    handleClearConversations,
    handleImportConversations,
    handleExportData,
  } = useContext(ChatbarContext);

  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseDown = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        window.addEventListener('mouseup', handleMouseUp);
      }
    };

    const handleMouseUp = (e: MouseEvent) => {
      window.removeEventListener('mouseup', handleMouseUp);
      setIsProfileDropdownOpen(false);
    };

    window.addEventListener('mousedown', handleMouseDown);

    return () => {
      window.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  return (
    <div className="flex flex-col items-center space-y-1 border-t border-white/20 pt-1 text-sm">
      {conversations.length > 0 ? (
        <ClearConversations onClearConversations={handleClearConversations} />
      ) : null}

      <Import onImport={handleImportConversations} />

      <SidebarButton
        text={t('Export data')}
        icon={<IconFileExport size={18} />}
        onClick={() => handleExportData()}
      />

      <SidebarButton
        text={t('Settings')}
        icon={<IconSettings size={18} />}
        onClick={() => setIsSettingDialog(true)}
      />
      <SettingDialog
        open={isSettingDialogOpen}
        onClose={() => {
          setIsSettingDialog(false);
        }}
      />

      <div className="w-full relative">
        <div
          ref={modalRef}
          className={`bg-black transition-all absolute flex bottom-0 w-full rounded ${
            isProfileDropdownOpen ? '' : 'h-0 hidden'
          }
          `}
        >
          <LogoutButton></LogoutButton>
        </div>
      </div>
      {isAuthenticated ? (
        <SidebarButton
          text={user?.name || ''}
          textClassName="flex-grow text-left"
          icon={
            <img
              src={user?.picture}
              alt={user?.name}
              style={{ maxWidth: '40px', flexGrow: 1 }}
            />
          }
          iconRight={
            <IconDots className="text-gray-600" size="1.2em"></IconDots>
          }
          onClick={() => {
            setIsProfileDropdownOpen((v) => !v);
          }}
        ></SidebarButton>
      ) : null}
    </div>
  );
};
