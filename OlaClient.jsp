<%@page import="java.util.ArrayList"%>
<%@page import="java.util.Arrays"%>
<%@page import="java.lang.reflect.Array"%>
<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
	pageEncoding="ISO-8859-1"%>
<%@ page
	import="java.net.URL"%>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>Insert title here</title>

</head>
<body>
	<form action="https://www.cdslolao.com/NewCustomer/HOLEN/REFID/0" method="get">

		<input id="olaButton" type="submit" value="Click" name="Click" />
	</form>
	<%
		String uri = request.getScheme() + "://" + // "http" + "://
				request.getServerName() + // "myhost"
				":" + // ":"
				request.getServerPort() + // "8080"
				request.getRequestURI() + // "/people"
				"?" + // "?"
				request.getQueryString();
		String OLAOKey = "HOLEN";
		String RefId = "REFID";
		
		URL myURL = null;
		
		if (uri != null) {
			try {
				myURL = new URL(uri);
				String s = myURL.getQuery();
				String[] value = null;
				int index = s.indexOf("status");
				String ss = s.substring(index);
				String[] arr = ss.split("&");
				//System.out.println("arr--" + Arrays.toString(arr));
				ArrayList<String> l = new ArrayList<String>();
				for (int i = 0; i < arr.length; i++) {
					value = arr[i].split("=");//value[i] will be value i+1th value
					l.add(i, value[1]);
				}
				
				String key = l.get(0);
				String refId1 = l.get(1);
				String etoken1 = l.get(2);
				if (key != null) {
					if (key.equalsIgnoreCase("AuthToken")) {
						String Url1 = "https://www.cdslolao.com/NewCustomer/" + OLAOKey + "/" + refId1 + "/" + etoken1;
						response.sendRedirect(Url1);
					}
				}
				//}
				
			} catch (Exception e) {
				System.out.println("Connection timed out or Connection failed");

			}
		}
	%>

</body>
</html>