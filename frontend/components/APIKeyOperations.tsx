import React, { useState } from "react";
import { ExclamationCircleOutlined, CopyOutlined } from "@ant-design/icons";
import { Dropdown, Modal, Typography, message, Input, Button } from "antd";
import { generateCurlCommand } from "../utils/api-keys";

const { Paragraph } = Typography;

const strToArr = (str: string) =>
  str.length
    ? str
        .replace(/^,+|,+$/g, "")
        .split(",")
        .map(Number)
    : undefined;

export const APIKeyOperations = ({
  prompt: initialPrompt,
  apiKey,
  url,
  onDelete,
}) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [prompt, setPrompt] = useState(initialPrompt);
  const [uids, setUids] = useState("");

  const handleMenuClick = ({ key }) => {
    if (key === "copyCurl") {
      setModalVisible(true);
    }
  };

  const handleCopyCurl = () => {
    const curlCommand = generateCurlCommand({
      prompt,
      apiKey,
      url,
      uids: strToArr(uids),
    });
    navigator.clipboard.writeText(curlCommand);
    message.success("Curl command copied to clipboard!");
  };

  const showDeleteConfirm = (actuallyDelete) => {
    Modal.confirm({
      title: "Are you sure you want to delete this item?",
      icon: <ExclamationCircleOutlined />,
      content: (
        <>
          <Paragraph>This action cannot be undone.</Paragraph>
          <Paragraph>
            <pre>{apiKey}</pre>
          </Paragraph>
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
    <>
      <Dropdown.Button
        menu={{
          items: [{ key: "copyCurl", label: "Create example request" }],
          onClick: handleMenuClick,
        }}
        onClick={() => showDeleteConfirm(onDelete)}
      >
        Delete
      </Dropdown.Button>
      <Modal
        title="Make a Request"
        visible={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="copy" type="primary" onClick={handleCopyCurl}>
            <CopyOutlined /> Copy
          </Button>,
        ]}
      >
        <Input
          placeholder="Prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          style={{ marginBottom: 10 }}
        />
        <Input
          placeholder="UIDs (optional, comma-separated)"
          value={uids}
          onChange={(e) => setUids(e.target.value)}
          style={{ marginBottom: 10 }}
        />
        <Paragraph>
          <pre>
            {generateCurlCommand({
              prompt,
              apiKey,
              url,
              uids: strToArr(uids),
            })}
          </pre>
        </Paragraph>
      </Modal>
    </>
  );
};
