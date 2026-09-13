import { BrowserRouter, Routes, Route } from "react-router-dom"
import AppLayout from "@/components/AppLayout"
import InvestigatePage from "@/pages/InvestigatePage"
import ReportPage from "@/pages/ReportPage"
import FinancialDataPage from "@/pages/FinancialDataPage"
import HistoryPage from "@/pages/HistoryPage"
import DataSourcesPage from "@/pages/DataSourcesPage"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<InvestigatePage />} />
          <Route path="report" element={<ReportPage />} />
          <Route path="financial-data" element={<FinancialDataPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="data-sources" element={<DataSourcesPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App