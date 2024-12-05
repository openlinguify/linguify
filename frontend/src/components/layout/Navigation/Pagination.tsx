import React from "react";
import { Pagination } from "react-bootstrap";

const CustomPagination = ({
  totalPages,
  currentPage,
  handlePageChange,
}: {
  totalPages: number;
  currentPage: number;
  handlePageChange: (page: number) => void;
}) => {
  return (
    <Pagination className="justify-content-center">
      {Array.from({ length: totalPages }, (_, i) => i + 1).map((number) => (
        <Pagination.Item
          key={number}
          active={number === currentPage}
          onClick={() => handlePageChange(number)}
        >
          {number}
        </Pagination.Item>
      ))}
    </Pagination>
  );
};

export default CustomPagination;
