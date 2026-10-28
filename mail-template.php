<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>HTML email template</title>
	<style>
		
		*{
			margin: 0;
			padding: 0;
			box-sizing: border-box;
		}

		body{
			font-family: sans-serif;
			min-height: 100vh;
		}

		.page{
			width: 768px;
			margin:  0 auto;
			font-size: 16px;
			color: #555555;
		}

		h1{
			background-color: #f4f4f4;
			padding: 20px;
			margin-top: 20px;
		}

		h2{
			padding: 20px;
		}

		p{
			padding: 10px 20px;
			line-height: 26px;
		}	

		h3{
			padding: 20px;
		}

		table{
			padding: 20px;
			width:  100%;
		}

		table tr{}
		table th{
			text-align: left;
			padding: 10px;
			background-color: #e4e4e4;
		}
		table td{
			border: thin solid #d4d4d4;
			padding: 10px;
		}

		footer{
			padding: 20px;
		}

		footer a{
			text-decoration: none;
			color: #155197;
		}
	</style>
</head>
<body>
	<div class="page">
		
		<h1>Thank you for your purchase</h1>

		<h2>From: e-electronics</h2>
		<p>
			Lorem ipsum dolor sit amet, consectetur, adipisicing elit. Numquam, dicta earum incidunt labore minima sequi fuga? Architecto voluptates <strong>voluptatibus nam dolore sint, consequuntur</strong> dignissimos doloribus exercitationem ullam incidunt reprehenderit, eaque fuga quas. Ea dolorum architecto iusto vel.
		</p>
		<p>
			Lorem ipsum dolor sit amet, consectetur, adipisicing elit. Numquam, dicta earum incidunt labore minima sequi fuga? Architecto voluptates voluptatibus nam dolore sint, consequuntur dignissimos doloribus exercitationem ullam incidunt reprehenderit, eaque fuga quas. Ea dolorum architecto iusto vel.
		</p>


		<h3>Products</h3>
		<table>
			<tr>
				<th>Product</th>
				<th>Price</th>
				<th>Discount</th>
			</tr>
			<tr>
				<td>Product A</td>
				<td>20.00 &euro;</td>
				<td>10%</td>
			</tr>
			<tr>
				<td>Product B</td>
				<td>40.00 &euro;</td>
				<td>10%</td>
			</tr>
			<tr>
				<td><strong>Total</strong></td>
				<td><strong>54.00 &euro;</strong></td>
				<td><strong>6.00 &euro;</strong></td>
			</tr>
		</table>

		<footer>
			<a href="https://google.com">Hyperlink</a> |
			<a href="https://digitalfox-tutoroals.com">Hyperlink</a> |
			<a href="">Hyperlink</a> |
			<a href="">Hyperlink</a>
		</footer>
	</div>
</body>
</html>