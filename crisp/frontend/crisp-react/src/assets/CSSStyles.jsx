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
        
        html, body, #root {
            margin: 0;
            padding: 0;
            min-height: 100vh;
            background-color: var(--light-gray);
            color: var(--text-dark);
        }
        
        .App {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header */
        header {
            background-color: var(--white);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: relative;
            top: 0;
            z-index: 100;
            flex-shrink: 0;
        }
        
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            min-height: 70px;
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
            display: block;
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
            color: var(--primary-blue);
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
            transition: all 0.3s ease;
            border: none;
            background: none;
            font-family: inherit;
        }
        
        .notifications:hover {
            background-color: var(--light-gray);
            transform: scale(1.05);
        }
        
        .notifications i {
            font-size: 18px;
            color: var(--text-muted);
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
        }
        
        .user-actions {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-left: 15px;
        }
        
        .user-actions .btn {
            padding: 6px 12px;
            font-size: 13px;
            min-width: auto;
        }
        
        .user-actions .btn i {
            margin-right: 4px;
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
            color: var(--primary-blue);
        }
        
        .user-role {
            font-size: 12px;
            color: var(--text-muted);
        }
        
        /* Register button */
        .register-button {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 6px;
            color: var(--text-muted);
            font-size: 14px;
            transition: all 0.3s;
            margin-left: 15px;
            cursor: pointer;
        }
        
        .register-button:hover {
            background-color: var(--light-gray);
            color: var(--primary-blue);
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

        /* Notifications Container */
        .notifications-container {
            position: relative;
        }

        /* Notifications Dropdown */
        .notifications-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            width: 360px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            border: 1px solid var(--medium-gray);
            z-index: 1000;
            margin-top: 8px;
            max-height: 500px;
            overflow: hidden;
        }

        .dropdown-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            border-bottom: 1px solid var(--medium-gray);
            background: var(--light-gray);
        }

        .dropdown-header h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: var(--text-dark);
        }

        .close-btn {
            background: none;
            border: none;
            cursor: pointer;
            color: var(--text-muted);
            padding: 4px;
            border-radius: 4px;
            transition: all 0.2s;
        }

        .close-btn:hover {
            background: var(--medium-gray);
            color: var(--text-dark);
        }

        .notifications-list {
            max-height: 300px;
            overflow-y: auto;
        }

        .notification-item {
            display: flex;
            padding: 12px 20px;
            border-bottom: 1px solid var(--light-gray);
            cursor: pointer;
            transition: all 0.2s;
        }

        .notification-item:hover {
            background: var(--light-gray);
        }

        .notification-item.unread {
            background: #f8f9ff;
            border-left: 3px solid var(--primary-blue);
        }

        .notification-item.read {
            opacity: 0.8;
        }

        .notification-icon {
            margin-right: 12px;
            color: var(--primary-blue);
        }

        .notification-content {
            flex: 1;
        }

        .notification-title {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
            color: var(--text-dark);
        }

        .notification-message {
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 4px;
            line-height: 1.4;
        }

        .notification-time {
            font-size: 11px;
            color: var(--text-muted);
        }

        .no-notifications {
            padding: 20px;
            text-align: center;
            color: var(--text-muted);
            font-style: italic;
        }

        .dropdown-footer {
            padding: 12px 20px;
            border-top: 1px solid var(--medium-gray);
            background: var(--light-gray);
            text-align: center;
        }

        /* User Profile Container */
        .user-profile-container {
            position: relative;
        }

        .user-profile {
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            padding: 8px 12px;
            border-radius: 6px;
            transition: all 0.2s;
            border: none;
            background: none;
            font-family: inherit;
        }

        .user-profile:hover {
            background: var(--light-gray);
        }

        /* User Menu Dropdown */
        .user-menu-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            width: 280px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            border: 1px solid var(--medium-gray);
            z-index: 1000;
            margin-top: 8px;
            overflow: hidden;
        }

        .user-avatar-large {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: var(--primary-blue);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 18px;
            margin-right: 12px;
        }

        .user-name-large {
            font-weight: 600;
            font-size: 16px;
            color: var(--primary-blue);
        }

        .user-email {
            font-size: 14px;
            color: var(--text-muted);
        }

        .menu-divider {
            height: 1px;
            background: var(--medium-gray);
            margin: 8px 0;
        }

        .menu-items {
            padding: 8px 0;
        }

        .menu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            width: 100%;
            padding: 12px 20px;
            background: none;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
            color: var(--text-dark);
        }

        .menu-item:hover {
            background: var(--light-gray);
        }

        .menu-item i {
            width: 16px;
            color: var(--text-muted);
        }

        .menu-badge {
            background: var(--danger);
            color: white;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 10px;
            min-width: 18px;
            height: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: auto;
        }

        .logout-item {
            color: var(--danger);
        }

        .logout-item:hover {
            background: rgba(229, 62, 62, 0.1);
        }

        /* Submenu Styles */
        .menu-item-submenu {
            position: relative;
        }

        .submenu-arrow {
            margin-left: auto;
            font-size: 12px;
            transition: transform 0.2s;
        }

        .submenu {
            background: var(--light-gray);
            border-radius: 4px;
            margin: 4px 0;
            border-left: 3px solid var(--primary-blue);
        }

        .submenu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            width: 100%;
            padding: 10px 20px 10px 35px;
            border: none;
            background: none;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 13px;
            color: var(--text-dark);
        }

        .submenu-item:hover {
            background: var(--medium-gray);
        }

        .submenu-item i {
            width: 14px;
            color: var(--text-muted);
            font-size: 12px;
        }

        /* Notifications Grid */
        .notifications-grid {
            display: grid;
            gap: 16px;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            margin-top: 20px;
        }

        .notification-card {
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--primary-blue);
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }

        .notification-card:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }

        .notification-card.unread {
            border-left-color: var(--danger);
            background: #fefefe;
        }

        .notification-card.read {
            opacity: 0.8;
            border-left-color: var(--medium-gray);
        }

        .notification-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }

        .notification-icon {
            background: var(--light-blue);
            color: var(--primary-blue);
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }

        .notification-meta {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 4px;
        }

        .notification-type {
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 12px;
            text-transform: uppercase;
        }

        .notification-type.critical {
            background: rgba(229, 62, 62, 0.1);
            color: var(--danger);
        }

        .notification-type.warning {
            background: rgba(246, 173, 85, 0.1);
            color: var(--warning);
        }

        .notification-type.info {
            background: rgba(66, 153, 225, 0.1);
            color: var(--info);
        }

        .notification-type.update,
        .notification-type.alert {
            background: var(--light-blue);
            color: var(--primary-blue);
        }

        .notification-time {
            font-size: 12px;
            color: var(--text-muted);
        }

        .notification-content h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--text-dark);
        }

        .notification-content p {
            font-size: 14px;
            color: var(--text-muted);
            line-height: 1.4;
            margin: 0;
        }

        .notification-badge {
            position: absolute;
            top: 8px;
            right: 8px;
        }

        .unread-indicator {
            width: 8px;
            height: 8px;
            background: var(--danger);
            border-radius: 50%;
            display: block;
        }

        .no-notifications {
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px 20px;
        }

        .no-notifications-content i {
            font-size: 48px;
            color: var(--medium-gray);
            margin-bottom: 16px;
        }

        .no-notifications-content h3 {
            font-size: 18px;
            color: var(--text-dark);
            margin-bottom: 8px;
        }

        .no-notifications-content p {
            color: var(--text-muted);
        }

        /* Alert styles */
        .alert {
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }

        .alert-error {
            background: rgba(229, 62, 62, 0.1);
            color: var(--danger);
            border: 1px solid rgba(229, 62, 62, 0.2);
        }

        .alert-success {
            background: rgba(56, 161, 105, 0.1);
            color: var(--success);
            border: 1px solid rgba(56, 161, 105, 0.2);
        }

        /* Form rows */
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }

        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
        }

        /* Profile tabs */
        .profile-tabs {
            display: flex;
            border-bottom: 1px solid var(--medium-gray);
            margin-bottom: 24px;
        }

        .tab-button {
            background: none;
            border: none;
            padding: 12px 24px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            font-size: 14px;
            font-weight: 500;
            color: var(--text-muted);
        }

        .tab-button.active {
            color: var(--primary-blue);
            border-bottom-color: var(--primary-blue);
        }

        .tab-button:hover {
            color: var(--text-dark);
        }

        /* Loading states */
        .loading-spinner,
        .loading-notifications {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 20px;
            color: var(--text-muted);
            font-style: italic;
        }

        /* Alert cards for alerts page */
        .alerts-grid {
            display: grid;
            gap: 16px;
        }

        .alert-card {
            background: white;
            border-radius: 8px;
            padding: 16px;
            border-left: 4px solid;
        }

        .alert-card.critical {
            border-left-color: var(--danger);
        }

        .alert-card.warning {
            border-left-color: var(--warning);
        }

        .alert-card.info {
            border-left-color: var(--info);
        }

        .alert-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }

        .alert-header i {
            font-size: 18px;
        }

        .alert-card.critical .alert-header i {
            color: var(--danger);
        }

        .alert-card.warning .alert-header i {
            color: var(--warning);
        }

        .alert-card.info .alert-header i {
            color: var(--info);
        }

        .alert-header h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
        }

        .alert-time {
            font-size: 12px;
            color: var(--text-muted);
        }

        .alert-actions {
            margin-top: 12px;
            display: flex;
            gap: 8px;
        }

        /* Notifications page */
        .notifications-page-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .notification-page-item {
            background: white;
            border-radius: 8px;
            padding: 16px;
            display: flex;
            gap: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .notification-page-item:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .notification-page-item.unread {
            background: #f8f9ff;
            border-left: 3px solid var(--primary-blue);
        }

        .notification-page-item.read {
            opacity: 0.8;
        }

        .notification-icon-profile {
            color: var(--primary-blue);
        }

        .notification-content-profile {
            flex: 1;
        }

        /* User management table */
        .user-management-table {
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }

        .table-header {
            display: grid;
            grid-template-columns: 2fr 2fr 1fr 1fr 1fr;
            background: var(--light-gray);
            padding: 16px;
            font-weight: 600;
            border-bottom: 1px solid var(--medium-gray);
        }

        .table-row {
            display: grid;
            grid-template-columns: 2fr 2fr 1fr 1fr 1fr;
            padding: 16px;
            border-bottom: 1px solid var(--light-gray);
            align-items: center;
        }

        .table-cell {
            padding: 0 8px;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }

        .badge.admin {
            background: var(--primary-blue);
            color: white;
        }

        .status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }

        .status.active {
            background: rgba(56, 161, 105, 0.1);
            color: var(--success);
        }

        /* Main Navigation */
        nav.main-nav {
            background-color: var(--primary-blue);
            padding: 0;
            flex-shrink: 0;
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
            transition: all 0.3s ease;
            position: relative;
            cursor: pointer;
            user-select: none;
        }
        
        .nav-links a i {
            font-size: 14px;
        }
        
        .nav-links a:hover {
            background-color: rgba(255, 255, 255, 0.1);
            transform: translateY(-1px);
        }
        
        .nav-links a.active {
            background-color: rgba(255, 255, 255, 0.2);
            font-weight: 600;
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
            flex: 1;
            min-height: calc(100vh - 130px); /* Account for header and nav height */
        }
        
        /* Page Section */
        .page-section {
            display: none;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .page-section.active {
            display: block;
            opacity: 1;
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
            transition: all 0.3s ease;
            border: none;
            text-decoration: none;
            user-select: none;
            white-space: nowrap;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
        
        .btn:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
            min-height: 120px; /* Ensure minimum height for visibility */
        }
        
        @media (max-width: 1200px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .stat-card {
            background-color: var(--white);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            border: 1px solid var(--medium-gray);
            min-height: 120px;
            position: relative;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
            border-color: var(--primary-blue);
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
        
        @media (max-width: 1024px) {
            .nav-links a {
                padding: 16px 15px;
                font-size: 13px;
            }
            
            .nav-links a i {
                display: none;
            }
        }
        
        @media (max-width: 768px) {
            .header-container {
                flex-wrap: wrap;
                gap: 10px;
            }
            
            .search-bar {
                order: 3;
                width: 100%;
            }
            
            .search-bar input {
                width: 100%;
            }
            
            .nav-links {
                flex-wrap: wrap;
            }
            
            .nav-links a {
                padding: 12px 10px;
                font-size: 12px;
            }
            
            .user-actions .btn {
                padding: 4px 8px;
                font-size: 12px;
            }
            
            .profile-grid {
                grid-template-columns: 1fr;
            }
            
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .profile-tabs {
                flex-wrap: wrap;
            }
            
            .tab-button {
                flex: 1;
                min-width: 120px;
            }
        }
        
        @media (max-width: 480px) {
            .nav-links {
                justify-content: center;
            }
            
            .nav-links a {
                padding: 10px 8px;
                min-width: 80px;
                text-align: center;
            }
        }
        
        /* Ensure page sections are properly displayed */
        .page-section {
            display: none;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .page-section.active {
            display: block;
            opacity: 1;
        }
        
        /* Loading state for smooth transitions */
        .page-section.loading {
            opacity: 0.5;
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


        /* User Profile Styles */
        .profile-tabs {
            display: flex;
            border-bottom: 2px solid var(--medium-gray);
            margin-bottom: 24px;
        }
        
        .tab-button {
            padding: 12px 20px;
            border: none;
            background: none;
            color: var(--text-muted);
            font-weight: 500;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .tab-button:hover {
            color: var(--primary-blue);
            background: var(--light-blue);
        }
        
        .tab-button.active {
            color: var(--primary-blue);
            border-bottom-color: var(--primary-blue);
        }
        
        .profile-content {
            margin-top: 24px;
        }
        
        .profile-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
        }
        
        .profile-form {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        
        .form-group label {
            font-weight: 600;
            font-size: 14px;
            color: var(--text-dark);
        }
        
        .form-group input, 
        .form-group select,
        .form-group textarea {
            padding: 10px 12px;
            border: 1px solid var(--medium-gray);
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--primary-blue);
        }
        
        .form-group input:disabled {
            background: var(--light-gray);
            color: var(--text-muted);
        }
        
        .form-hint {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
        }
        
        .account-stats {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .stat-item:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            font-weight: 500;
            color: var(--text-muted);
        }
        
        .stat-value {
            font-weight: 600;
            color: var(--text-dark);
        }
        
        /* Notification List in Profile */
        .notifications-list-profile {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .notification-item-profile {
            display: flex;
            padding: 16px;
            border: 1px solid var(--medium-gray);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
        }
        
        .notification-item-profile:hover {
            border-color: var(--primary-blue);
            box-shadow: 0 2px 8px rgba(0, 86, 179, 0.1);
        }
        
        .notification-item-profile.unread {
            background: rgba(0, 86, 179, 0.02);
            border-color: var(--primary-blue);
        }
        
        .notification-icon-profile {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: var(--light-blue);
            color: var(--primary-blue);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 16px;
            flex-shrink: 0;
        }
        
        .notification-content-profile {
            flex: 1;
            position: relative;
        }
        
        .notification-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }
        
        .notification-item-profile .notification-title {
            font-weight: 600;
            font-size: 15px;
            color: var(--text-dark);
        }
        
        .notification-item-profile .notification-time {
            font-size: 12px;
            color: var(--text-muted);
            white-space: nowrap;
        }
        
        .notification-item-profile .notification-message {
            font-size: 14px;
            color: var(--text-muted);
            line-height: 1.4;
        }
        
        .unread-indicator {
            position: absolute;
            top: 8px;
            right: 8px;
            width: 8px;
            height: 8px;
            background: var(--primary-blue);
            border-radius: 50%;
        }
        
        .no-notifications-profile {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
        }
        
        .no-notifications-profile i {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        .no-notifications-profile p {
            font-size: 16px;
            margin: 0;
        }
        
        /* Security Settings */
        .security-section {
            padding: 20px 0;
            border-bottom: 1px solid var(--medium-gray);
        }
        
        .security-section:last-child {
            border-bottom: none;
        }
        
        .security-section h3 {
            margin: 0 0 8px 0;
            font-size: 16px;
            color: var(--text-dark);
        }
        
        .security-section .text-muted {
            margin-bottom: 12px;
            color: var(--text-muted);
        }
        
        .session-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: var(--light-gray);
            border-radius: 6px;
            margin-top: 12px;
        }
        
        .session-device {
            font-weight: 600;
            color: var(--text-dark);
        }
        
        .session-details {
            font-size: 13px;
            color: var(--text-muted);
        }

        /* User Management Styles */
        .access-denied {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
            padding: 40px;
        }
        
        .access-denied-content {
            text-align: center;
            color: var(--text-muted);
        }
        
        .access-denied-content i {
            font-size: 64px;
            margin-bottom: 20px;
            color: var(--danger);
        }
        
        .user-stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 24px;
        }
        
        .user-filters {
            display: flex;
            gap: 16px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .search-input, .filter-select {
            padding: 10px 12px;
            border: 1px solid var(--medium-gray);
            border-radius: 6px;
            font-size: 14px;
        }
        
        .user-cell {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: var(--primary-blue);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
        }
        
        .role-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .role-administrator {
            background: rgba(229, 62, 62, 0.1);
            color: var(--danger);
        }
        
        .role-analyst {
            background: rgba(0, 160, 233, 0.1);
            color: var(--info);
        }
        
        .role-user {
            background: rgba(56, 161, 105, 0.1);
            color: var(--success);
        }
        
        .action-buttons-table {
            display: flex;
            gap: 8px;
        }
        
        .btn-icon {
            width: 32px;
            height: 32px;
            border: none;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
            background: var(--light-gray);
            color: var(--text-muted);
        }
        
        .btn-icon:hover {
            transform: translateY(-1px);
        }
        
        .btn-icon.btn-danger {
            background: rgba(229, 62, 62, 0.1);
            color: var(--danger);
        }
        
        /* Modal Styles */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        
        .modal-content {
            background: white;
            border-radius: 8px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 90%;
        }
        
        .modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--medium-gray);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-body {
            padding: 24px;
        }
        
        .modal-footer {
            padding: 16px 24px;
            border-top: 1px solid var(--medium-gray);
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }
        }
      `}
    </style>
  );
}

export default CSSStyles;