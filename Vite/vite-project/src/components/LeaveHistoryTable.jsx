import { 
  Card, CardHeader, CardBody, Divider, Table, TableHeader, 
  TableColumn, TableBody, TableRow, TableCell, Chip, Skeleton 
} from "@heroui/react";

const LeaveHistoryTable = ({ data, loading }) => {
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'danger';
      default: return 'default';
    }
  };

  return (
    <Card className="shadow-sm xl:col-span-3">
      <CardHeader className="px-6 pt-6 pb-2 flex justify-between items-center">
        <h2 className="text-xl font-bold text-slate-800">Leave History</h2>
      </CardHeader>
      <Divider className="opacity-50" />
      <CardBody className="px-2 sm:px-4">
        <Table isStriped aria-label="Leave History" removeWrapper shadow="none" className="min-w-full">
          <TableHeader>
            <TableColumn className="bg-transparent text-gray-400">ID</TableColumn>
            <TableColumn className="bg-transparent text-gray-400">BEGIN</TableColumn>
            <TableColumn className="bg-transparent text-gray-400">END</TableColumn>
            <TableColumn className="bg-transparent text-gray-400">TYPE</TableColumn>
            <TableColumn className="bg-transparent text-gray-400">STATUS</TableColumn>
          </TableHeader>
          <TableBody emptyContent={!loading && "No records found."}>
            {loading ? (
              Array.from({ length: 5 }).map((_, index) => (
                <TableRow key={index}>
                  <TableCell><Skeleton className="h-3 w-8 rounded-lg" /></TableCell>
                  <TableCell><Skeleton className="h-3 w-20 rounded-lg" /></TableCell>
                  <TableCell><Skeleton className="h-3 w-20 rounded-lg" /></TableCell>
                  <TableCell><Skeleton className="h-3 w-16 rounded-lg" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-16 rounded-full" /></TableCell>
                </TableRow>
              ))
            ) : (
              data.map((item) => (
                <TableRow key={item.LeaveApplicationId}>
                  <TableCell className="font-bold">{item.LeaveApplicationId}</TableCell>
                  <TableCell className="text-xs">{item.BeginDate}</TableCell>
                  <TableCell className="text-xs">{item.EndDate}</TableCell>
                  <TableCell className="text-xs">{item.TimeOffType}</TableCell>
                  <TableCell>
                    <Chip size="sm" color={getStatusColor(item.ApprovalStatus)} variant="dot" className="border-none font-bold uppercase">
                      {item.ApprovalStatus}
                    </Chip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardBody>
    </Card>
  );
};

export default LeaveHistoryTable;