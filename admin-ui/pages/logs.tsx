import { useEffect, useState, useRef } from "react";
import { Table, Input, Button, Space, InputRef, Badge } from "antd";
import Highlighter from "react-highlight-words";
import { SearchOutlined } from "@ant-design/icons";
import useSWR from "swr";
import fetcher from "../utils/fetcher";
import { FilterDropdownProps } from "antd/es/table/interface";
import { DateTime } from "luxon";

function renderErrorCell(isError: boolean, errorText: string) {
  return (
    <Space wrap={false}>
      <Badge color={isError ? "red" : "green"}></Badge>
      {errorText}
    </Space>
  );
}

export default function Logs() {
  const { data, error } = useSWR("/admin/logs/", fetcher);

  const [searchText, setSearchText] = useState<React.Key>("");
  const [searchedColumn, setSearchedColumn] = useState("");
  const searchInput = useRef<InputRef>(null);

  const getColumnSearchProps = (dataIndex) => ({
    filterDropdown: ({
      setSelectedKeys,
      selectedKeys,
      confirm,
      clearFilters,
      close,
    }: FilterDropdownProps) => (
      <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
        <Input
          ref={searchInput}
          placeholder={`Search ${dataIndex}`}
          value={selectedKeys[0]}
          onChange={(e) =>
            setSelectedKeys(e.target.value ? [e.target.value] : [])
          }
          onPressEnter={() => handleSearch(selectedKeys, confirm, dataIndex)}
          style={{ marginBottom: 8, display: "block" }}
        />
        <Space>
          <Button
            type="primary"
            onClick={() => handleSearch(selectedKeys, confirm, dataIndex)}
            icon={<SearchOutlined />}
            size="small"
            style={{ width: 90 }}
          >
            Search
          </Button>
          <Button
            onClick={() => handleReset(clearFilters)}
            size="small"
            style={{ width: 90 }}
          >
            Reset
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => {
              confirm({ closeDropdown: false });
              setSearchText(selectedKeys[0]);
              setSearchedColumn(dataIndex);
            }}
          >
            Filter
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => {
              close();
            }}
          >
            close
          </Button>
        </Space>
      </div>
    ),
    filterIcon: (filtered) => (
      <SearchOutlined style={{ color: filtered ? "#1677ff" : undefined }} />
    ),
    onFilter: (value, record) => {
      if (record === undefined) return false;
      if (record[dataIndex] === undefined) return false;
      if (record[dataIndex] === null) return false;
      return record[dataIndex]
        .toLowerCase()
        .trim()
        .includes((value || "").toLowerCase().trim());
    },
    onFilterDropdownOpenChange: (visible) => {
      if (visible) {
        setTimeout(() => searchInput.current?.select(), 100);
      }
    },
    render: (text) =>
      searchedColumn === dataIndex ? (
        <Highlighter
          highlightStyle={{ backgroundColor: "#ffc069", padding: 0 }}
          searchWords={[searchText]}
          autoEscape
          textToHighlight={text ? text.toString() : ""}
        />
      ) : (
        text?.trim()
      ),
  });

  const handleSearch = (selectedKeys, confirm, dataIndex) => {
    confirm();
    setSearchText(selectedKeys[0]);
    setSearchedColumn(dataIndex);
  };

  const handleReset = (clearFilters) => {
    clearFilters();
    setSearchText("");
  };

  const logsData = data
    ? data.map((d) => {
        return {
          ...d,
          prompt: JSON.stringify(d.prompt),
        };
      })
    : [];

  const columns = [
    {
      title: "Timestamp",
      dataIndex: "timestamp",
      key: "timestamp",
      sorter: (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
      ...getColumnSearchProps("timestamp"),
      render: (text) => (
        <span>
          {text}
          <br></br>
          {DateTime.fromSeconds(text).toFormat("yyyy-MM-dd HH:mm:ss")}
        </span>
      ),
    },
    {
      title: "Status",
      key: "status",
      render(text, record) {
        let isError = !(record.is_api_success && record.is_success);
        return renderErrorCell(
          isError,
          record.api_error || record.return_message
        );
      },
    },
    {
      title: "Prompt",
      dataIndex: "prompt",
      key: "prompt",

      ...getColumnSearchProps("prompt"),
    },
    {
      title: "Response",
      dataIndex: "response",
      key: "response",
      ...getColumnSearchProps("response"),
    },
    {
      title: "Responder Hotkey",
      dataIndex: "responder_hotkey",
      key: "responder_hotkey",
      ...getColumnSearchProps("responder_hotkey"),
    },
    {
      title: "API Key Id",
      dataIndex: "api_key",
      key: "api_key",
      ...getColumnSearchProps("api_key"),
    },
  ];

  return (
    <div>
      <Table
        columns={columns}
        dataSource={logsData}
        rowKey="timestamp"
        scroll={{
          x: true,
        }}
      />
    </div>
  );
}
