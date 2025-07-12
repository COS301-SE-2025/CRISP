import React from 'react';

function CSSStyles() {
  return (
    <style>
      {`
        :root {
            --primary-blue: #0056b3;
            --secondary-blue: #007bff;
            --light-blue: #e8f4ff;
            --accent-blue: #00a0e9;
            --dark-blue: #003366;
            --white: #ffffff;
            --light-gray: #f5f7fa;
            --medium-gray: #e2e8f0;
            --text-dark: #2d3748;
            --text-muted: #718096;
            --danger: #e53e3e;
            --success: #38a169;
            --warning: #f6ad55;
            --info: #4299e1;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: var(--light-gray);
            color: var(--text-dark);
            min-height: 100vh;
            overflow-x: hidden;
            width: 100%;
        }
        
        html {
            width: 100%;
            overflow-x: hidden;
        }
        
        #root {
            width: 100%;
            min-height: 100vh;
        }
        
        .App {
            width: 100%;
            min-height: 100vh;
        }
        
        .container {
            max-width: none;
            width: 100%;
            margin: 0;
            padding: 0 20px;
        }
        
        /* Header */
        header {
            background-color: var(--white);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--primary-blue);
            text-decoration: none;
        }
        
        .logo-image {
            height: 40px;
            width: auto;
        }
        
        .logo-icon {
            font-size: 24px;
            background-color: var(--primary-blue);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .logo-text {
            font-weight: 700;
            font-size: 22px;
        }
        
        .nav-actions {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .search-bar {
            position: relative;
        }
        
        .search-bar input {
            padding: 8px 12px 8px 36px;
            border-radius: 6px;
            border: 1px solid var(--medium-gray);
            width: 240px;
            background-color: var(--light-gray);
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .search-bar input:focus {
            width: 280px;
            outline: none;
            border-color: var(--secondary-blue);
            background-color: var(--white);
        }
        
        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }
        
        .notifications {
            position: relative;
            cursor: pointer;
            padding: 8px;
            border-radius: 6px;
            transition: background-color 0.3s;
        }
        
        .notifications:hover {
            background-color: var(--light-gray);
        }
        
        .notification-count {
            position: absolute;
            top: -5px;
            right: -5px;
            background-color: var(--danger);
            color: white;
            font-size: 10px;
            font-weight: 700;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .user-profile {
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            position: relative;
            padding: 8px;
            border-radius: 6px;
            transition: background-color 0.3s;
        }
        
        .user-profile:hover {
            background-color: var(--light-gray);
        }
        
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--primary-blue);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 16px;
        }
        
        .user-info {
            display: flex;
            flex-direction: column;
        }
        
        .user-name {
            font-weight: 600;
            font-size: 14px;
        }
        
        .user-role {
            font-size: 12px;
            color: var(--text-muted);
        }
        
        /* Logout button */
        .logout-button {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 6px;
            color: var(--text-muted);
            font-size: 14px;
            transition: all 0.3s;
            margin-left: 10px;
            cursor: pointer;
        }
        
        .logout-button:hover {
            background-color: var(--light-gray);
            color: var(--danger);
        }
        
        /* Dropdown Styles */
        .notifications-dropdown, .user-dropdown {
            position: absolute;
            top: calc(100% + 10px);
            right: 0;
            background-color: var(--white);
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            min-width: 280px;
            z-index: 200;
            border: 1px solid var(--medium-gray);
        }
        
        .dropdown-header {
            padding: 12px 16px;
            border-bottom: 1px solid var(--medium-gray);
            font-weight: 600;
            color: var(--text-dark);
            background-color: var(--light-gray);
            border-radius: 8px 8px 0 0;
        }
        
        .dropdown-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            cursor: pointer;
            transition: background-color 0.3s;
            color: var(--text-dark);
        }
        
        .dropdown-item:hover {
            background-color: var(--light-blue);
        }
        
        .dropdown-item.logout-item {
            color: var(--danger);
        }
        
        .dropdown-item.logout-item:hover {
            background-color: rgba(229, 62, 62, 0.1);
        }
        
        .dropdown-divider {
            height: 1px;
            background-color: var(--medium-gray);
            margin: 8px 0;
        }
        
        .dropdown-footer {
            padding: 12px 16px;
            border-top: 1px solid var(--medium-gray);
            text-align: center;
        }
        
        .dropdown-footer a {
            color: var(--primary-blue);
            text-decoration: none;
            font-size: 14px;
        }
        
        .dropdown-footer a:hover {
            text-decoration: underline;
        }
        
        .notification-item {
            padding: 12px 16px;
            border-bottom: 1px solid var(--medium-gray);
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .notification-item:hover {
            background-color: var(--light-blue);
        }
        
        .notification-item:last-child {
            border-bottom: none;
        }
        
        .notification-content strong {
            display: block;
            margin-bottom: 4px;
            color: var(--text-dark);
        }
        
        .notification-content p {
            margin: 0;
            color: var(--text-muted);
            font-size: 14px;
            margin-bottom: 4px;
        }
        
        .notification-time {
            font-size: 12px;
            color: var(--text-muted);
        }

        /* Main Navigation */
        nav.main-nav {
            background-color: var(--primary-blue);
            padding: 0;
        }
        
        .nav-container {
            display: flex;
            justify-content: space-between;
        }
        
        .nav-links {
            display: flex;
            list-style: none;
        }
        
        .nav-links li {
            position: relative;
        }
        
        .nav-links a {
            color: var(--white);
            text-decoration: none;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
            transition: background-color 0.3s;
            position: relative;
            cursor: pointer;
        }
        
        .nav-links a:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        .nav-links a.active {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .nav-links a.active::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background-color: var(--accent-blue);
        }
        
        .nav-right {
            display: flex;
            align-items: center;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            color: var(--white);
            padding: 0 20px;
            font-size: 14px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--success);
        }
        
        /* Main Content */
        .main-content {
            padding: 30px 0;
            width: 100%;
            min-height: calc(100vh - 140px);
        }
        
        /* Page Section */
        .page-section {
            display: none;
            width: 100%;
        }
        
        .page-section.active {
            display: block;
            width: 100%;
        }
        
        /* Dashboard Header */
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .page-title {
            font-size: 24px;
            font-weight: 600;
            color: var(--dark-blue);
        }
        
        .page-subtitle {
            color: var(--text-muted);
            margin-top: 4px;
            font-size: 15px;
        }
        
        .action-buttons {
            display: flex;
            gap: 12px;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
        }
        
        .btn-primary {
            background-color: var(--primary-blue);
            color: white;
        }
        
        .btn-primary:hover {
            background-color: var(--dark-blue);
        }
        
        .btn-secondary {
            background-color: var(--secondary-blue);
            color: white;
        }
        
        .btn-secondary:hover {
            background-color: var(--primary-blue);
        }
        
        .btn-outline {
            background-color: transparent;
            border: 1px solid var(--primary-blue);
            color: var(--primary-blue);
        }
        
        .btn-outline:hover {
            background-color: var(--light-blue);
        }
        
        .btn-danger {
            background-color: var(--danger);
            color: white;
        }
        
        .btn-danger:hover {
            background-color: #c53030;
        }
        
        .btn-sm {
            padding: 6px 12px;
            font-size: 13px;
        }
        
        /* Stats Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background-color: var(--white);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        
        .stat-title {
            color: var(--text-muted);
            font-size: 14px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stat-icon {
            width: 28px;
            height: 28px;
            background-color: var(--light-blue);
            color: var(--primary-blue);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: var(--dark-blue);
            margin-bottom: 5px;
        }
        
        .stat-change {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 14px;
        }
        
        .increase {
            color: var(--success);
        }
        
        .decrease {
            color: var(--danger);
        }
        
        /* Main Grid */
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
            width: 100%;
        }
        
        .card {
            background-color: var(--white);
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            overflow: hidden;
            margin-bottom: 24px;
        }
        
        .card:last-child {
            margin-bottom: 0;
        }
        
        .card-header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--medium-gray);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--dark-blue);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-icon {
            color: var(--primary-blue);
        }
        
        .card-actions {
            display: flex;
            gap: 12px;
        }
        
        .card-content {
            padding: 20px;
        }
        
        /* Tables */
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th, 
        .data-table td {
            padding: 12px 15px;
            text-align: left;
        }
        
        .data-table th {
            background-color: var(--light-gray);
            color: var(--text-muted);
            font-weight: 600;
            font-size: 14px;
        }
        
        .data-table tbody tr {
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .data-table tbody tr:last-child {
            border-bottom: none;
        }
        
        .data-table tbody tr:hover {
            background-color: var(--light-blue);
        }
        
        /* Badge Styles */
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .badge-high {
            background-color: rgba(229, 62, 62, 0.1);
            color: var(--danger);
        }
        
        .badge-medium {
            background-color: rgba(246, 173, 85, 0.1);
            color: var(--warning);
        }
        
        .badge-low {
            background-color: rgba(56, 161, 105, 0.1);
            color: var(--success);
        }
        
        .badge-active {
            background-color: rgba(56, 161, 105, 0.1);
            color: var(--success);
        }
        
        .badge-inactive {
            background-color: rgba(113, 128, 150, 0.1);
            color: var(--text-muted);
        }
        
        .badge-connected {
            background-color: rgba(66, 153, 225, 0.1);
            color: var(--info);
        }
        
        .badge-tags {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }
        
        /* Filter Section */
        .filters-section {
            background-color: var(--light-gray);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }
        
        .filters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .filter-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
        }
        
        .filter-control {
            display: flex;
            gap: 10px;
        }
        
        .filter-control select,
        .filter-control input {
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--medium-gray);
            font-size: 14px;
            flex: 1;
        }
        
        .filter-control select:focus,
        .filter-control input:focus {
            outline: none;
            border-color: var(--secondary-blue);
        }
        
        /* Institutions List */
        .institution-list {
            list-style: none;
        }
        
        .institution-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 0;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .institution-item:last-child {
            border-bottom: none;
        }
        
        .institution-logo {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background-color: var(--light-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary-blue);
            font-weight: 600;
        }
        
        .institution-details {
            flex: 1;
        }
        
        .institution-name {
            font-weight: 600;
            margin-bottom: 2px;
        }
        
        .institution-meta {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        .institution-stats {
            display: flex;
            gap: 15px;
            margin-top: 5px;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 13px;
        }
        
        .stat-item i {
            color: var(--primary-blue);
        }
        
        .trust-level {
            width: 80px;
            height: 6px;
            background-color: var(--medium-gray);
            border-radius: 3px;
        }
        
        .trust-fill {
            height: 100%;
            border-radius: 3px;
            background-color: var(--primary-blue);
        }
        
        /* Activity Stream */
        .activity-stream {
            list-style: none;
        }
        
        .activity-item {
            padding: 15px 0;
            display: flex;
            gap: 15px;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background-color: var(--light-blue);
            color: var(--primary-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        
        .activity-details {
            flex: 1;
        }
        
        .activity-text {
            margin-bottom: 5px;
            line-height: 1.4;
        }
        
        .activity-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .activity-time {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        /* MITRE ATT&CK Matrix */
        .matrix-container {
            overflow-x: auto;
        }
        
        .mitre-matrix {
            min-width: 900px;
            border-collapse: collapse;
        }
        
        .mitre-matrix th {
            background-color: var(--primary-blue);
            color: white;
            padding: 12px;
            text-align: center;
            font-size: 14px;
        }
        
        .matrix-cell {
            width: 100px;
            height: 60px;
            border: 1px solid var(--medium-gray);
            padding: 10px;
            font-size: 12px;
            vertical-align: top;
            position: relative;
            transition: all 0.3s;
        }
        
        .matrix-cell:hover {
            background-color: var(--light-blue);
        }
        
        .matrix-cell.active {
            background-color: rgba(0, 86, 179, 0.1);
        }
        
        .technique-count {
            position: absolute;
            top: 5px;
            right: 5px;
            background-color: var(--primary-blue);
            color: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
        }
        
        /* Reports Section */
        .report-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        
        .report-card {
            background-color: var(--white);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .report-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        
        .report-header {
            padding: 20px;
            background-color: var(--light-blue);
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .report-type {
            display: inline-block;
            padding: 4px 10px;
            background-color: var(--primary-blue);
            color: white;
            font-size: 12px;
            font-weight: 600;
            border-radius: 20px;
            margin-bottom: 10px;
        }
        
        .report-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--dark-blue);
        }
        
        .report-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-muted);
            font-size: 13px;
        }
        
        .report-content {
            padding: 20px;
        }
        
        .report-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .report-stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 24px;
            font-weight: 700;
            color: var(--dark-blue);
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        .report-actions {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }
        
        /* Feed Items */
        .feed-items {
            list-style: none;
        }
        
        .feed-item {
            display: flex;
            gap: 16px;
            padding: 16px 0;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .feed-item:last-child {
            border-bottom: none;
        }
        
        .feed-icon {
            width: 48px;
            height: 48px;
            border-radius: 8px;
            background-color: var(--light-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary-blue);
            font-size: 20px;
            flex-shrink: 0;
        }
        
        .feed-details {
            flex: 1;
        }
        
        .feed-name {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--dark-blue);
        }
        
        .feed-description {
            color: var(--text-muted);
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .feed-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }
        
        .feed-stats {
            display: flex;
            gap: 15px;
        }
        
        .feed-badges {
            display: flex;
            gap: 8px;
        }
        
        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 5px;
            margin-top: 20px;
        }
        
        .page-item {
            width: 32px;
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .page-item:hover {
            background-color: var(--light-blue);
        }
        
        .page-item.active {
            background-color: var(--primary-blue);
            color: white;
        }
        
        /* Chart Containers */
        .chart-container {
            height: 300px;
            position: relative;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            border-bottom: 1px solid var(--medium-gray);
            margin-bottom: 20px;
        }
        
        .tab {
            padding: 12px 20px;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .tab:hover {
            color: var(--primary-blue);
        }
        
        .tab.active {
            color: var(--primary-blue);
            border-bottom-color: var(--primary-blue);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Helper classes */
        .text-danger {
            color: var(--danger);
        }
        
        .text-success {
            color: var(--success);
        }
        
        .text-warning {
            color: var(--warning);
        }
        
        .text-muted {
            color: var(--text-muted);
        }
        
        .mt-4 {
            margin-top: 16px;
        }
        
        .mb-4 {
            margin-bottom: 16px;
        }
        
        /* Responsive Design */
        @media (max-width: 1200px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .report-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 992px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .nav-links a {
                padding: 16px 10px;
                font-size: 14px;
            }
            
            .search-bar input {
                width: 160px;
            }
            
            .search-bar input:focus {
                width: 200px;
            }
            
            .status-indicator {
                display: none;
            }
            
            .report-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 576px) {
            .header-container {
                flex-direction: column;
                gap: 15px;
            }
            
            .nav-actions {
                width: 100%;
                justify-content: center;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .page-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }
        }


        /* Register button */
        .register-button {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 6px;
            color: var(--primary-blue);
            font-size: 14px;
            transition: all 0.3s;
            margin-right: 10px;
            cursor: pointer;
        }
        
        .register-button:hover {
            background-color: var(--light-blue);
        }

        .logo-image {
        height: 30px;
        width: auto;
        max-width: 100%;
        }

        /* User Profile Styles */
        .profile-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }

        .profile-main, .profile-sidebar {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        .profile-form {
            display: grid;
            gap: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .form-group label {
            font-weight: 600;
            color: var(--text-dark);
        }

        .form-group input, .form-group select, .form-group textarea {
            padding: 12px;
            border: 1px solid var(--medium-gray);
            border-radius: 8px;
            font-size: 14px;
        }

        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgba(0, 86, 179, 0.1);
        }

        .form-group input:disabled {
            background-color: var(--light-gray);
            cursor: not-allowed;
        }

        .form-actions {
            display: flex;
            gap: 15px;
            justify-content: flex-end;
            margin-top: 20px;
        }

        .sessions-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .session-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background-color: var(--light-gray);
            border-radius: 8px;
            border: 1px solid var(--medium-gray);
        }

        .session-info {
            flex: 1;
        }

        .session-device {
            font-weight: 600;
            margin-bottom: 5px;
        }

        .session-ip, .session-time {
            font-size: 13px;
            color: var(--text-muted);
        }

        .activity-stats {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }

        .stat-item {
            text-align: center;
            padding: 20px;
            background-color: var(--light-blue);
            border-radius: 8px;
        }

        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--primary-blue);
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .change-password-form {
            margin-top: 20px;
            padding: 20px;
            background-color: var(--light-gray);
            border-radius: 8px;
            border: 1px solid var(--medium-gray);
        }

        .error-message {
            color: var(--danger);
            background-color: rgba(229, 62, 62, 0.1);
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 15px;
            font-size: 14px;
        }

        /* Trust Management Styles */
        .trust-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }

        .trust-main, .trust-sidebar {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        .trust-level-bar {
            position: relative;
            width: 100%;
            height: 20px;
            background-color: var(--medium-gray);
            border-radius: 10px;
            overflow: hidden;
        }

        .trust-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--danger) 0%, var(--warning) 50%, var(--success) 100%);
            transition: width 0.3s ease;
        }

        .trust-percentage {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 12px;
            font-weight: 600;
            color: var(--white);
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        }

        .trust-groups-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .trust-group-card {
            padding: 20px;
            background-color: var(--white);
            border-radius: 12px;
            border: 1px solid var(--medium-gray);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .group-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .group-header h3 {
            font-size: 18px;
            color: var(--text-dark);
        }

        .group-description {
            color: var(--text-muted);
            margin-bottom: 20px;
            line-height: 1.5;
        }

        .group-stats {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }

        .group-stats .stat-item {
            background-color: var(--light-blue);
            padding: 10px;
            border-radius: 6px;
            text-align: center;
            flex: 1;
        }

        .group-actions {
            display: flex;
            gap: 10px;
        }

        .trust-stats {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }

        /* User Management Styles */
        .user-stats-grid {
            margin-top: 30px;
        }

        .filters-section {
            margin: 30px 0;
            padding: 20px;
            background-color: var(--white);
            border-radius: 12px;
            border: 1px solid var(--medium-gray);
        }

        .filters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .filter-label {
            font-weight: 600;
            color: var(--text-dark);
            font-size: 14px;
        }

        .filter-control input, .filter-control select {
            padding: 10px;
            border: 1px solid var(--medium-gray);
            border-radius: 6px;
            font-size: 14px;
        }

        /* Alerts System Styles */
        .alerts-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }

        .alerts-main, .alerts-sidebar {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        .service-info {
            display: grid;
            gap: 15px;
        }

        .info-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--medium-gray);
        }

        .info-item:last-child {
            border-bottom: none;
        }

        .info-item label {
            font-weight: 600;
            color: var(--text-dark);
        }

        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-badge.success {
            background-color: var(--success);
            color: var(--white);
        }

        .status-badge.error {
            background-color: var(--danger);
            color: var(--white);
        }

        .test-email-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .alert-settings {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .setting-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background-color: var(--light-gray);
            border-radius: 8px;
            border: 1px solid var(--medium-gray);
        }

        .setting-info h4 {
            margin-bottom: 5px;
            color: var(--text-dark);
        }

        .setting-info p {
            color: var(--text-muted);
            font-size: 14px;
        }

        .setting-control {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .email-stats {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }

        .recent-alerts {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .alert-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            background-color: var(--light-gray);
            border-radius: 8px;
            border: 1px solid var(--medium-gray);
        }

        .alert-icon {
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: var(--primary-blue);
            color: var(--white);
            border-radius: 50%;
        }

        .alert-info {
            flex: 1;
        }

        .alert-text {
            font-weight: 600;
            margin-bottom: 5px;
        }

        .alert-time {
            font-size: 13px;
            color: var(--text-muted);
        }

        .text-success {
            color: var(--success);
        }

        .text-error {
            color: var(--danger);
        }

        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px;
            color: var(--text-muted);
        }

        /* Modal Styles */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        .modal {
            background-color: var(--white);
            border-radius: 12px;
            width: 90%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid var(--medium-gray);
        }

        .modal-header h3 {
            margin: 0;
            color: var(--text-dark);
        }

        .modal-close {
            background: none;
            border: none;
            font-size: 24px;
            color: var(--text-muted);
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background-color 0.2s;
        }

        .modal-close:hover {
            background-color: var(--medium-gray);
        }

        .modal-body {
            padding: 20px;
        }

        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 15px;
            padding: 20px;
            border-top: 1px solid var(--medium-gray);
        }

        /* Responsive Design */
        @media (max-width: 1200px) {
            .profile-grid, .trust-grid, .alerts-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            .trust-groups-grid {
                grid-template-columns: 1fr;
            }
            
            .filters-grid {
                grid-template-columns: 1fr;
            }
            
            .group-stats {
                flex-direction: column;
                gap: 10px;
            }
            
            .setting-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }
        }
        }
      `}
    </style>
  );
}

export default CSSStyles;