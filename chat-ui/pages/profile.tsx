import { useAuth0 } from '@auth0/auth0-react';
import { IconArrowBack, IconEdit, IconTrash } from '@tabler/icons-react';

import Head from 'next/head';
import Image from 'next/image';
import { useRouter } from 'next/router';

import { title } from '@/utils/app/const';

import Spinner from '@/components/Spinner';

import { DateTime } from 'luxon';

const apiKeys = [
  {
    id: '1',
    api_key: 'rGp44wdyik8fJvnfNv4rHgkTyOLXPBxYTKA86wdsZfPqe3yKucrlkxn0oA8EOH_z',
    api_key_hint: '...OH_z',
    name: 'New API Key',
    request_count: '0',
    valid_until: '1687816800',
    credits: '-1',
    enabled: '0',
    rate_limits: null,
    created_at: '1687015275',
    updated_at: '1687024970',
    api_request_count: '0',
    rate_limits_enabled: '0',
  },
  {
    id: '2',
    api_key: 'rm-z_EljnCoi6O3BoAgU98tYKGwBt_uO8ueoCp0uYTcTYnsodZPnYYJPQ1ga7Gt7',
    api_key_hint: '...7Gt7',
    name: 'New API Key',
    request_count: '0',
    valid_until: '-1',
    credits: '-1',
    enabled: '1',
    rate_limits: null,
    created_at: '1687015350',
    updated_at: '1687015350',
    api_request_count: '0',
    rate_limits_enabled: '0',
  },
];

const Profile = () => {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuth0();

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="Manage Usage & API Keys" />
        <meta
          name="viewport"
          content="height=device-height ,width=device-width, initial-scale=1, user-scalable=no"
        />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main
        className={`flex h-screen w-screen flex-col text-sm bg-[#202123] text-white dark:text-white p-6`}
      >
        <div className="container max-w-2xl mx-auto bg-[#343541] text-white p-4 rounded-md">
          {/* Back arrow and profile title */}
          <div className="flex items-center mb-4 text-4xl">
            <button
              onClick={() => {
                router.back();
              }}
              className="mr-4"
            >
              <IconArrowBack size="1em" />
            </button>
            <h1>My profile</h1>
          </div>

          {/* User details */}
          <div className="mb-6 flex justify-center flex-col items-center ">
            <div></div>
            {isLoading ? (
              <div className="rounded-full w-[100px] h-[100px] bg-slate-500"></div>
            ) : (
              <Image
                className="rounded-full"
                src={user?.picture!}
                alt={user?.name || 'Profile Picture'}
                width={100}
                height={100}
              />
            )}
            <div className="text-xl mt-4">
              {isLoading ? (
                <Spinner className="border-t-white h-7 w-7" />
              ) : (
                <p>{user?.name}</p>
              )}
            </div>
          </div>

          {/* Lifetime Usage and API keys */}
          <section className="mb-6">
            {/* <h2>Lifetime-Usage</h2> */}
            {/* Content related to Lifetime-Usage */}
          </section>

          <section>
            <h2 className="text-lg">API keys</h2>
            <table className="table-auto w-full text-sm text-left">
              <thead className="text-xs uppercase ">
                <tr>
                  <th className="px-4 py-1">Name</th>
                  <th className="px-4 py-1">Key</th>
                  <th className="px-4 py-1">Created</th>
                  <th className="px-4 py-1">Credits</th>
                  <th className="px-4 py-1">Requests</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {apiKeys.map((key) => (
                  <tr key={key.id}>
                    <td className="px-4 py-1">{key.name}</td>
                    <td className="px-4 py-1">{key.api_key_hint}</td>
                    <td className="px-4 py-1">
                      {DateTime.fromSeconds(Number(key.created_at)).toFormat(
                        'MMM dd, yyyy',
                      )}
                    </td>
                    <td className="px-4 py-1">{key.credits}</td>
                    <td className="px-4 py-1">{key.api_request_count}</td>
                    <td className="px-4 py-1 flex">
                      <button className="hover:bg-slate-600 p-1 rounded-md">
                        <IconEdit size="1em"></IconEdit>
                      </button>
                      <button className="hover:bg-slate-600 p-1 rounded-md ml-2">
                        <IconTrash size="1em"></IconTrash>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      </main>
    </>
  );
};

export default Profile;
