import React, { useState } from "react";
import { ExclamationCircleOutlined, CopyOutlined } from "@ant-design/icons";
import {
  Dropdown,
  Modal,
  Typography,
  message,
  Input,
  Button,
  Radio,
  InputNumber,
  Form,
  Space,
} from "antd";
import { generateCurlCommand } from "../utils/api-keys";

const { Paragraph, Title } = Typography;

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
  const [top_n, setTopN] = useState(1);
  const [selection, setSelection] = useState("unspecified");

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
      uids: selection === "uids" ? strToArr(uids) : undefined,
      top_n: selection === "topN" ? top_n : undefined,
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
        title="Generate a curl snippet to make a request to the API"
        visible={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="copy" type="primary" onClick={handleCopyCurl}>
            <CopyOutlined /> Copy
          </Button>,
        ]}
      >
        <Form layout="vertical">
          <Form.Item label="Prompt" help="The prompt to ask miners for">
            <Input
              placeholder="Prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </Form.Item>
          <Form.Item
            label="Query strategy"
            style={{ marginBottom: ".5rem", marginTop: "2rem" }}
          >
            <Radio.Group
              style={{ marginTop: 0 }}
              onChange={(e) => setSelection(e.target.value)}
              value={selection}
            >
              <Radio.Button value="topN">Top miners</Radio.Button>
              <Radio.Button value="uids">Specific UIDs</Radio.Button>
              <Radio.Button value="unspecified">Unspecified</Radio.Button>
            </Radio.Group>
          </Form.Item>
          {selection === "uids" && (
            <Form.Item help="Query specific UIDs.">
              <Input
                placeholder="UIDs (comma-separated)"
                value={uids}
                onChange={(e) => setUids(e.target.value)}
              />
            </Form.Item>
          )}
          {selection === "topN" && (
            <Form.Item help="Query top miners based on incentive. Set to 1 to only query the top miner. If set to for example 5, the top 5 miners will be queried with the same prompt in parallel.">
              <InputNumber
                min={1}
                style={{ width: "100%" }}
                placeholder="Top miners"
                value={top_n}
                onChange={(e) => e !== null && setTopN(e)}
              />
            </Form.Item>
          )}
          {selection === "unspecified" && (
            <Paragraph>
              If unspecified the default uid specified by the validator endpoint
              will be selected.
            </Paragraph>
          )}
        </Form>
        <Paragraph style={{ marginTop: "3rem" }}>
          <Title level={5}>Curl command</Title>
          <pre>
            {generateCurlCommand({
              prompt,
              apiKey,
              url,
              uids: selection === "uids" ? strToArr(uids) : undefined,
              top_n: selection === "topN" ? top_n : undefined,
            })}
          </pre>
        </Paragraph>
      </Modal>
    </>
  );
};
