import { ExclamationCircleOutlined } from "@ant-design/icons";
import { Dropdown, Modal, Typography, message } from "antd";
import { generateCurlCommand } from "../utils/api-keys";

const { Text } = Typography;
const items = [{ key: "copyCurl", label: "Copy curl example" }];

export const APIKeyOperations = ({
  prompt,
  apiKey,
  url,
  onDelete,
}: {
  prompt: string;
  apiKey: string;
  url: string;
  onDelete: () => void;
}) => {
  const handleMenuClick = ({ key }) => {
    if (key === "copyCurl") {
      const curlCommand = generateCurlCommand({ prompt, apiKey, url });
      navigator.clipboard.writeText(curlCommand);
      message.success("Curl command copied to clipboard!");
    }
  };

  const showDeleteConfirm = (actuallyDelete) => {
    Modal.confirm({
      title: "Are you sure you want to delete this item?",
      icon: <ExclamationCircleOutlined />,
      content: (
        <>
          <Text ellipsis code>
            {apiKey}
          </Text>
          <p>This action cannot be undone.</p>
        </>
      ),
      okText: "Yes",
      okType: "danger",
      cancelText: "No",
      onOk() {
        actuallyDelete();
      },
    });
  };

  return (
    <Dropdown.Button
      menu={{ items, onClick: handleMenuClick }}
      onClick={() => showDeleteConfirm(onDelete)}
    >
      Delete
    </Dropdown.Button>
  );
};
